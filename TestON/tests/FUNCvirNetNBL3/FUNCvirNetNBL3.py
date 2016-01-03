"""
Description: This test is to determine if North bound
    can handle the request

List of test cases:
CASE1 - Variable initialization and optional pull and build ONOS package
CASE2 - Create Router northbound test
CASE3 - Update Router northbound test
CASE4 - Delete Router northbound test
CASE5 - Create RouterInterface northbound test
CASE6 - Delete RouterInterface northbound test
CASE7 - Create Floatingip northbound test
CASE8 - Update Floatingip northbound test
CASE9 - Delete Floatingip northbound test
CASE10 - Create Gateway northbound test
CASE11 - Update Gateway northbound test
CASE12 - Delete Gateway northbound test

lanqinglong@huawei.com
"""
import os
import new
import json

class FUNCvirNetNBL3:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        cell<name>
        onos-verify-cell
        NOTE:temporary - onos-remove-raft-logs
        onos-uninstall
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start vtnrsc
        """

        import time
        import os
        main.log.info( "ONOS Single node Start "+
                      "VirtualNet Northbound test - initialization" )
        main.case( "Setting up test environment" )
        main.caseExplanation  = "Setup the test environment including "+\
                                "installing ONOS,start ONOS."

        # load some variables from the params file
        PULLCODE = False
        if main.params['GIT']['pull'] =='True':
            PULLCODE = True
        gitBranch = main.params['GIT']['branch']
        cellName = main.params['ENV']['cellName']
        ipList = os.getenv( main.params['CTRL']['ip1'] )

        main.step("Create cell file and apply to environment")
        cellAppString = main.params['ENV']['cellApps']
        main.ONOSbench.createCellFile(main.ONOSbench.ip_address,cellName,
                                      main.Mininet1.ip_address,
                                      cellAppString,ipList )

        cellResult = main.ONOSbench.setCell(cellName)
        verifyResult = main.ONOSbench.verifyCell()

        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )

        #FIXME:this is short term fix
        main.log.info( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()

        main.CLIs = []
        main.nodes = []
        main.numCtrls=1
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )

        for i in range ( 1, main.numCtrls +1):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str(i) ) )
                main.nodes.append( getattr( main, 'ONOS' + str(i) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break
       	
        main.log.info( "Uninstalling ONOS" )
        for node in main.nodes:
            main.ONOSbench.onosUninstall( node.ip_address )

        #Make sure ONOS is DEAD
        main.log.info( "Killing any ONOS processes" )
        killResults = main.TRUE
        for node in main.nodes:
            killed = main.ONOSbench.onosKill( node.ip_address )
            killResults = killResults and killed

        cleanInstallResult = main.TRUE
        gitPullResult = main.TRUE
        main.log.info( "Git checkout and pull " + gitBranch )
        if PULLCODE:
            main.ONOSbench.gitCheckout ( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()
            # values of 1 or 3 are good
            utilities.assert_lesser ( expect=0, actual=gitPullResult,
                                      onpass="Git pull successful",
                                      onfail ="Git pull failed" )
        main.ONOSbench.getVersion( report =True )
        main.step( "Using mvn clean install" )
        cleanInstallResult= main.TRUE
        if PULLCODE and gitPullResult == main.TRUE:
            cleanInstallResult = main.ONOSbench.cleanInstall()
        else:
            main.log.warn("Did not pull new code so skipping mvn "+
                          "clean install")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=cleanInstallResult,
                                 onpass="MCI successful",
                                 onfail="MCI failed" )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=packageResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package " )
        time.sleep( main.startUpSleep )

        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall(
            options="-f",node=main.nodes[0].ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=onosInstallResult,
                                onpass="ONOS install successful",
                                onfail="ONOS install failed" )
        time.sleep( main.startUpSleep )

        main.step( "Checking if ONOS is up yet" )

        for i in range( 2 ):
            onos1Isup =  main.ONOSbench.isup( main.nodes[0].ip_address )
            if onos1Isup:
                break
        utilities.assert_equals( expect=main.TRUE, actual=onos1Isup,
                     onpass="ONOS startup successful",
                     onfail="ONOS startup failed" )
        time.sleep( main.startUpSleep )
        
        main.log.step( "Starting ONOS CLI sessions" )
        serviceResults = main.ONOSbench.onosStart(main.nodes[0].ip_address)
        utilities.assert_equals( expect=main.TRUE, actual=serviceResults,
                                onpass="ONOS service startup successful",
                                onfail="ONOS service startup failed" )
        time.sleep( main.startUpSleep )

        print main.nodes[0].ip_address
        cliResults = main.ONOScli1.startOnosCli(main.nodes[0].ip_address)
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                onpass="ONOS cli startup successful",
                                onfail="ONOS cli startup failed" )
        time.sleep( main.startUpSleep )
	
        main.step( "App Ids check" )
        appCheck = main.ONOScli1.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                     onpass="App Ids seem to be correct",
                     onfail="Something is wrong with app Ids" )

        if cliResults == main.FALSE:
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanup()
            main.exit()

        main.step( "Install org.onosproject.vtn app" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.vtn" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                     onpass="Install org.onosproject.vtn successful",
                     onfail="Install org.onosproject.vtn app failed" )

        time.sleep( main.startUpSleep )

 
    def CASE2( self, main ):

        """
        Test Post Router
        """
        import os
        import json

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()


        main.log.info( "ONOS Router Post test Start" )
        main.case( "Virtual Network NBI Test - Router" )
        main.caseExplanation = "Test Router Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        router = RouterData()
        router.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        router.tenant_id = network.tenant_id

        networkpostdata = network.DictoJson()
        routerpostdata = router.DictoJson()

        main.step( "Post Network Data via HTTP(Post Router need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post Router Success",
                onfail="Post Router Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Router Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, router.id, path + 'routers/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Router Success",
                onfail="Get Router Failed " + str( Getstatus ) + "," + str( result ) )

        IDcmpresult = router.JsonCompare( routerpostdata, result, 'router', 'id' )
        TanantIDcmpresult = router.JsonCompare( routerpostdata, result, 'router', 'tenant_id' )

        main.step( "Compare Post Router Data via HTTP" )
        Cmpresult = IDcmpresult and TanantIDcmpresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult ) )

        deletestatus,result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )
        
        deletestatus,result = main.ONOSrest.send( ctrlip, port, router.id, path+'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )

        if Cmpresult != True:
            main.log.error( "Post Router compare failed" )
 
 
    def CASE3( self, main ):

        """
        Test Update Router
        """
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Router Update test Start" )
        main.case( "Virtual Network NBI Test - Subnet" )
        main.caseExplanation = "Test Router Update NBI " +\
                                "Verify Stored Data is same with Update Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        router = RouterData()
        router.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        router.tenant_id = network.tenant_id
        router.name = "demo-router"
        networkpostdata = network.DictoJson()
        routerpostdata = router.DictoJson()

        #Change allocation_poolsdata scope
        router.name = "demo-router-new"
        #end change
        newrouterpostdata = router.DictoJson()

        main.step( "Post Network Data via HTTP(Post Router need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post Router Success",
                onfail="Post Router Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Update Router Data via HTTP" )
        Putstatus, result = main.ONOSrest.send( ctrlip, port, router.id, path + 'routers/',
                                                 'PUT', None, newrouterpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Putstatus,
                onpass="Update Router Success",
                onfail="Update Router Failed " + str( Putstatus ) + "," + str( result ) )

        main.step( "Get Router Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, router.id, path + 'routers/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Router Success", 
                onfail="Get Router Failed " + str( Getstatus ) + "," + str( result ) )

        IDcmpresult = router.JsonCompare( newrouterpostdata, result, 'router', 'id' )
        TanantIDcmpresult = router.JsonCompare( newrouterpostdata, result, 'router', 'tenant_id' )
        Routername = router.JsonCompare( newrouterpostdata, result, 'router', 'name' )

        main.step( "Compare Router Data" )
        Cmpresult = IDcmpresult and TanantIDcmpresult and Routername
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult ) + \
                       ",Pool compare:" + str( Routername ) )

        main.step( "Delete Router via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, port, router.id, path+'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed " + str( deletestatus ) + "," + str( result ) )


        if Cmpresult != True:
            main.log.error( "Update Router compare failed" )
        
         
    def CASE4( self, main ):

        """
        Test Delete Router
        """ 
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Router Delete test Start" )
        main.case( "Virtual Network NBI Test - Router" )
        main.caseExplanation = "Test Router Delete NBI " +\
                                "Verify Stored Data is Null after Delete"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']
         
        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        router = RouterData()
        router.id = 'e44bd655-e22c-4aeb-b1e9-ea1606875178'
        router.tenant_id = network.tenant_id
       	router.name = 'demo-router' 
        networkpostdata = network.DictoJson()
        routerpostdata = router.DictoJson()
       

 

        main.step( "Post Network Data via HTTP(Post Router need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post Router Success",
                onfail="Post Router Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Delete Router Data via HTTP" )
        Deletestatus, result = main.ONOSrest.send( ctrlip, port, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed " + str( Deletestatus ) + "," + str( result ) )

        main.step( "Get Router Data is NULL" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, router.id, path + 'routers/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='The Router does not exists',
                actual=result,
                onpass="Get Router Success",
                onfail="Get Router Failed " + str( Getstatus ) + str( result ) )

        if result != 'The Router does not exists':
            main.log.error( "Delete Router failed" )

 
    def CASE5( self, main ):

        """
        Test Post RouterInterface
        """
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import SubnetData
            
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import VirtualPortData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterInterfaceData
            
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS RouterInterface Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test RouterInterface Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '10000001'
        network.tenant_id = '10000000'
        router = RouterData()
        router.id = '10000010'
        router.tenant_id = network.tenant_id
        subnet = SubnetData()
        subnet.id = "10000002"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "10000003"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.device_id = router.id
        routerinterface = RouterInterfaceData()
        routerinterface.id = port.device_id
        routerinterface.subnet_id = port.subnet_id
        routerinterface.tenant_id = port.tenant_id
        routerinterface.port_id = port.id

        networkpostdata = network.DictoJson()
        routerpostdata = router.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()
        routerinterfacedata = routerinterface.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post router Success",
                onfail="Post router Failed " + str( Poststatus ) + "," + str( result ) )
                
        main.step( "Put RouterInterface Data via HTTP")
       
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/' +
                                                 router.id + '/add_router_interface/', 
                                                 'PUT', None, routerinterfacedata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post RouterInterface Success",
                onfail="Post RouterInterface Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get RouterInterface Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Port Success",
                onfail="Get Port Failed " + str( Getstatus ) + "," + str( result ) )

        main.step( "Compare Post Port Data" )
        IDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'id' )
        TanantIDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'tenant_id' )
        NetoworkIDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'network_id' )
        DeviceIDresult = subnet.JsonCompare( portpostdata, result, 'port', 'device_id' )

        Cmpresult = IDcmpresult and TanantIDcmpresult and NetoworkIDcmpresult and DeviceIDresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult ) + \
                       ",Network id compare:" + str( NetoworkIDcmpresult ) +\
                       ",Device id compare:" + str( DeviceIDresult ) )

        main.step( "Del RouterInterface Data via HTTP")
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/' +
                                                 router.id + '/remove_router_interface/',
                                                 'PUT', None, routerinterfacedata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Delete RouterInterface Success",
                onfail="Delete RouterInterface Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )
        
        if Cmpresult != True:
            main.log.error( "Post port compare failed" )


    def CASE6( self, main ):

        """
        Test Delete RouterInterface
        """
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import VirtualPortData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterInterfaceData           
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS RouterInterface Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test RouterInterface Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '10000001'
        network.tenant_id = '10000000'
        router = RouterData()
        router.id = '10000010'
        router.tenant_id = network.tenant_id
        subnet = SubnetData()
        subnet.id = '10000002' 
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = '10000003'
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.device_id = router.id
        routerinterface = RouterInterfaceData()
        routerinterface.id = port.device_id
        routerinterface.subnet_id = port.subnet_id
        routerinterface.tenant_id = port.tenant_id
        routerinterface.port_id = port.id

        networkpostdata = network.DictoJson()
        routerpostdata = router.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()
        routerinterfacedata = routerinterface.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post router Success",
                onfail="Post router Failed " + str( Poststatus ) + "," + str( result ) )
                
        main.step( "Post RouterInterface Data via HTTP")
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/' +
                                                 router.id + '/add_router_interface/', 
                                                 'PUT', None, routerinterfacedata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post RouterInterface Success",
                onfail="Post RouterInterface Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Del RouterInterface Data via HTTP")
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/' +
                                                 router.id + '/remove_router_interface/', 
                                                 'PUT', None, routerinterfacedata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Delete RouterInterface Success",
                onfail="Delete RouterInterface Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Delete Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'Delete', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Delete Port Success",
                onfail="Delete Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Port Data is NULL" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='VirtualPort is not found',
                actual=result,
                onpass="Get Port Success",
                onfail="Get Port Failed " + str( Getstatus ) + "," + str( result ) )

        if result != 'VirtualPort is not found':
            main.log.error( "Delete Port failed" )                    

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )
            

    def CASE7( self, main ):

        """
        Test Post FloatingIp
        """
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import VirtualPortData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import FloatingIpData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS FloatingIp Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test FloatingIp Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '10000001'
        network.tenant_id = '10000000'
        subnet = SubnetData()
        subnet.id = "10000002"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "10000003"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.device_Id = '91a546ea-8add-47e7-ad98-15677c74b337'


        router = RouterData()
        router.id = '10000005'
        router.tenant_id = network.tenant_id
        floatingip = FloatingIpData()
        floatingip.id = port.device_Id
        floatingip.floating_network_id = port.network_id
        floatingip.tenant_id = router.tenant_id
        floatingip.floating_ip_address = '10.0.0.4'
        floatingip.router_id = router.id
        floatingip.port_id = port.id
        floatingip.fixed_ip_address = '192.168.1.4' 
        

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()
        routerpostdata = router.DictoJson()
        floatingippostdata = floatingip.DictoJson()

        floatingip.port_id = None
        floatingip.fixed_ip_address = None
        #floatingip.floating_ip_address = None
        clefloatingippostdata = floatingip.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post Router Success",
                onfail="Post Router Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Get Port Success",
                onfail="Get Port Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post FloatingIp Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'floatingips/',
                                                 'POST', None, floatingippostdata )
        
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post FloatingIp Success",
                onfail="Post FloatingIp Failed " + str( Poststatus ) + "," + str( result ) ) 

        main.step( "Get Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Get Port Success",
                onfail="Get Port Failed " + str( Poststatus ) + "," + str( result ) )

       
        main.step( "Get FloatingIp Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'floatingips/',
                                                 'GET', None, None )
        
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get FloatingIp Success",
                onfail="Get FloatingIp Failed " + str( Getstatus ) + "," + str( result ) )
 
        main.step( "Get FloatingIp Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'floatingips/' + 
                      floatingip.id +'?fields=id&fields=tenant_id',
                                                 'GET', None, None )
       	
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get FloatingIp Success",
                onfail="Get FloatingIp Failed " + str( Getstatus ) + "," + str( result ) )

        main.step( "Compare Post FloatingIp Data" )
        IDcmpresult = subnet.JsonCompare( floatingippostdata, result, 'floatingip', 'id' )
        TanantIDcmpresult = subnet.JsonCompare( floatingippostdata, result, 'floatingip', 'tenant_id' )

        Cmpresult = IDcmpresult and TanantIDcmpresult 
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult )) 

        main.step( "Post FloatingIp Clean Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, floatingip.id, path + 'floatingips/',
                                                 'PUT', None, clefloatingippostdata )

        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post FloatingIp Clean Success",
                onfail="Post FloatingIp Clean Failed " + str( Poststatus ) + "," + str( result ) )
                       
        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )
        
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )

        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, floatingip.id, path + 'floatingips/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Floatingip Success" + str(deletestatus) + str(result),
                onfail="Delete Floatingip Failed" + str(deletestatus) + str(result) )
        
        if Cmpresult != True:
            main.log.error( "Post Floatingip compare failed" )

    def CASE8( self, main ):

        """
        Test Update FloatingIp
        """
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import VirtualPortData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import FloatingIpData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS FloatingIp Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test FloatingIp Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '10000001'
        network.tenant_id = '10000000'
        subnet = SubnetData()
        subnet.id = "10000002"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "10000003"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.device_Id = '91a546ea-8add-47e7-ad98-15677c74b337'


        router = RouterData()
        router.id = '10000005'
        router.tenant_id = network.tenant_id
        
        floatingip = FloatingIpData()
        floatingip.id = port.device_Id
        floatingip.floating_network_id = port.network_id
        floatingip.tenant_id = router.tenant_id
        floatingip.floating_ip_address = '10.0.0.4'
        floatingip.router_id = router.id
        floatingip.port_id = port.id
        floatingip.fixed_ip_address = '192.168.1.4'

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()
        routerpostdata = router.DictoJson()
        floatingippostdata = floatingip.DictoJson()
        
        #create update floatingip
        nport = VirtualPortData()
        nport.id = '10000006'
        nport.subnet_id = subnet.id
        nport.tenant_id = network.tenant_id
        nport.network_id = network.id
        nport.device_Id = '91a546ea-8add-47e7-ad98-15677c74b337'

        nportpostdata = nport.DictoJson()
       	floatingip.port_id = nport.id
        nfloatingippostdata = floatingip.DictoJson()
        #end

        floatingip.port_id = None
        floatingip.fixed_ip_address = None
        clefloatingippostdata = floatingip.DictoJson()


        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post Router Success",
                onfail="Post Router Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post FloatingIp Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'floatingips/',
                                                 'POST', None, floatingippostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post FloatingIp Success",
                onfail="Post FloatingIp Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Delete Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Delete Port Success",
                onfail="Post Delete Port Failed " + str( Poststatus ) + "," + str( result ) )


        main.step( "Post NewPort Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, nportpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post New Port Success", 
                onfail="Post New Port Failed " + str( Poststatus ) + "," + str( result ) )

        
        main.step( "Post NewFloatingIp Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, floatingip.id, path + 'floatingips/',
                                                 'PUT', None, nfloatingippostdata )
        
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post NewFloatingIp Success",
                onfail="Post NewFloatingIp Failed " + str( Poststatus ) + "," + str( result ) )        
        main.step( "Get NewFloatingIp Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'floatingips/' +
                      floatingip.id +'?fields=id&fields=tenant_id&fields=port_id',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get NewFloatingIp Success:",
                onfail="Get NewFloatingIp Failed " + str( Getstatus ) + "," + str( result ) )

        main.step( "Compare Post FloatingIp Data" )
        IDcmpresult = subnet.JsonCompare( nfloatingippostdata, result, 'floatingip', 'id' )
        TanantIDcmpresult = subnet.JsonCompare( nfloatingippostdata, result, 'floatingip', 'tenant_id' )
        PortIDcmpresult = subnet.JsonCompare( nfloatingippostdata, result, 'floatingip', 'port_id' )
        Cmpresult = IDcmpresult and TanantIDcmpresult and PortIDcmpresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult )) 


        main.step( "Post FloatingIp Clean Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, floatingip.id, path + 'floatingips/',
                                                 'PUT', None, clefloatingippostdata )

        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post FloatingIp Clean Success",
                onfail="Post FloatingIp Clean Failed " + str( Poststatus ) + "," + str( result ) )
                     
        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )
        
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )

        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, floatingip.id, path + 'floatingips/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Floatingip Success",
                onfail="Delete Floatingip Failed" )
        
        if Cmpresult != True:
            main.log.error( "Post Floatingip compare failed" )

    def CASE9( self, main ):

        """
        Test Delete FloatingIp
        """
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import VirtualPortData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import FloatingIpData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS FloatingIp Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test FloatingIp Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '10000001'
        network.tenant_id = '10000000'
        subnet = SubnetData()
        subnet.id = "10000002"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "10000003"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.device_Id = '91a546ea-8add-47e7-ad98-15677c74b337'


        router = RouterData()
        router.id = '10000005'
        router.tenant_id = network.tenant_id
        floatingip = FloatingIpData()
        floatingip.id = port.device_Id
        floatingip.floating_network_id = port.network_id
        floatingip.tenant_id = router.tenant_id
        floatingip.floating_ip_address = '10.0.0.4'
        floatingip.router_id = router.id
        floatingip.port_id = port.id
        floatingip.fixed_ip_address = '192.168.1.4'

 
        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()
        routerpostdata = router.DictoJson()
        floatingippostdata = floatingip.DictoJson()

        floatingip.port_id = None
        floatingip.fixed_ip_address = None
        clefloatingippostdata = floatingip.DictoJson()


        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post Router Success",
                onfail="Post Router Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post FloatingIp Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'floatingips/',
                                                 'POST', None, floatingippostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post FloatingIp Success",
                onfail="Post FloatingIp Failed " + str( Poststatus ) + "," + str( result ) )


        main.step( "Post FloatingIp Clean Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, floatingip.id, path + 'floatingips/',
                                                 'PUT', None, clefloatingippostdata )

        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post FloatingIp Clean Success",
                onfail="Post FloatingIp Clean Failed " + str( Poststatus ) + "," + str( result ) )
        
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, floatingip.id, path + 'floatingips/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Floatingip Success",
                onfail="Delete Floatingip Failed" )        
        
        main.step( "Get FloatingIp Data is NULL" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, floatingip.id, path + 'floatingips/',
                                                 'GET', None, None )
        
        utilities.assert_equals(
                expect='Floating IP does not exist!',
                actual=result,
                onpass="Get Floating IP Success",
                onfail="Get Floating IP Failed " + str( Getstatus ) + "," + str( result ) )

        if result != 'Floating IP does not exist!':
            main.log.error( "Delete Floatingip failed" )

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )
        
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )

        if Cmpresult != True:
            main.log.error( "Post Floatingip compare failed" )


    def CASE10( self, main ):
         
        """
        Test Post Gateway
        """
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import VirtualPortData
                       
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS RouterInterface Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test RouterInterface Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "9352e05c-58b8-4f2c-b4df-c20435ser56466"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.device_id = router.id
        router = RouterData()
        router.id = '00000000001'
        router.network_id = port.network_id
        router.tenant_id = network.tenant_id
        router.subnet_id = subnet.id
        router.ip_address = '192.168.212.3'
        #router.gw_port_id = port.id
        

        networkpostdata = network.DictoJson()
        routerpostdata = router.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post router Success",
                onfail="Post router Failed " + str( Poststatus ) + "," + str( result ) )
                

        main.step( "Get Gateway Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Gateway Success", 
                onfail="Get Gateway Failed " + str( Getstatus ) + "," + str( result ) )

        main.step( "Compare Post Gateway Data" )
        externalcmpresult = network.GatewayCompare(routerpostdata,result,'router','external_gateway_info','external_fixed_ips')

        Cmpresult = externalcmpresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:external_gateway_info compare:" + str( externalcmpresult ) )

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )
        
        if Cmpresult != True:
            main.log.error( "Post port compare failed" )
 
    def CASE11( self, main ):
         
        """
        Test Update Gateway
        """
        import os

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import VirtualPortData
                       
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS RouterInterface Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test RouterInterface Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "9352e05c-58b8-4f2c-b4df-c20435ser56466"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.device_id = router.id
        router = RouterData()
        router.id = '00000000001'
        router.network_id = port.network_id
        router.tenant_id = network.tenant_id
        router.subnet_id = subnet.id
        #router.ip_address = port.ip_address
        #router.gw_port_id = port.id
        

        networkpostdata = network.DictoJson()
        routerpostdata = router.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()
        
        #new post gateway data
        router.external_gateway_info = None
        router.ip_address = '192.168.0.3'
        newrouterpostdata = router.DictoJson()
        #end data

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post router Success",
                onfail="Post router Failed " + str( Poststatus ) + "," + str( result ) )
                
        main.step( "Post New Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'PUT', None, newrouterpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post New router Success",
                onfail="Post New router Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Gateway Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Gateway Success",
                onfail="Get Gateway Failed " + str( Getstatus ) + "," + str( result ) )

        main.step( "Compare Post Gateway Data" )
        externalcmpresult = network.GatewayCompare(newrouterpostdata,result,'router','external_gateway_info','external_fixed_ips')

        Cmpresult = externalcmpresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:external_gateway_info compare:" + str( externalcmpresult ) )

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )
        
        if Cmpresult != True:
            main.log.error( "Post port compare failed" )
 
 
    def CASE12( self, main ):
         
        """
        Test Delete Gateway 
        """
        import os
        import json

        try:
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import RouterData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNBL3.dependencies.Nbdata import VirtualPortData
                       
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS RouterInterface Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test RouterInterface Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "9352e05c-58b8-4f2c-b4df-c20435ser56466"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.device_id = router.id
        router = RouterData()
        router.id = '00000000001'
        router.network_id = port.network_id
        router.tenant_id = network.tenant_id
        router.subnet_id = subnet.id
        #router.ip_address = port.ip_address
        #router.gw_port_id = port.id
        

        networkpostdata = network.DictoJson()
        routerpostdata = router.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()

        #del gateway data
        
        #router.external_gateway_info = None
        delgatewaypostdata = router.NoneGateway(routerpostdata)
        #end data
        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post router Success",
                onfail="Post router Failed " + str( Poststatus ) + "," + str( result ) )
        
       
        main.step( "Post Del Gateway Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'PUT', None, delgatewaypostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post router Success",
                onfail="Post router Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Gateway Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Gateway Success",
                onfail="Get Gateway Failed " + str( Getstatus ) + "," + str( result ) )

        main.step( "If Gateway Data is NULL" )
      
        try:
            jsonresult = json.loads(result)  
        except ValueError:
            print "result is not JSON Type!"
        
        if jsonresult['router']['external_gateway_info'] == None:
            externalcmpresult = True
        Cmpresult = externalcmpresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:external_gateway_info compare:" + str( externalcmpresult ) )

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, router.id, path + 'routers/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Router Success",
                onfail="Delete Router Failed" )
        
        if Cmpresult != True:
            main.log.error( "Post port compare failed" )
 
 
 
 
 
 
 
 
 
 
 

