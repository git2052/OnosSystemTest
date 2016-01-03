"""
Description: This test is to check onos l3 set configuration and flows with ovsdb connection.

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Configure Network Subnet Port
CASE3: Test through East-West and South-North 
CASE4: Clear ovs configuration and host configuration
zhanghaoyu7@huawei.com
"""
import os

class FUNCovsdbtestL3:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        cell <name>
        onos-verify-cell
        NOTE: temporary - onos-remove-raft-logs
        onos-uninstall
        start mininet
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start ovsdb
        start vtn apps
        """
        import os
        main.log.info( "ONOS Single node start " +
                         "ovsdb test - initialization" )
        main.case( "Setting up test environment" )
        main.caseExplanation = "Setup the test environment including " +\
                                "installing ONOS, start ONOS."

        # load some variables from the params file
        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ipList = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        OVSDB1Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip1' ] )
        OVSDB2Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip2' ] )
        """
        main.step( "Create cell file" )
        cellAppString = main.params[ 'ENV' ][ 'cellApps' ]
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       main.OVSDB1.ip_address,
                                       cellAppString, ipList )

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.log.info( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        """
        main.CLIs = []
        main.nodes = []
        main.numCtrls= 1

        for i in range( 1, main.numCtrls + 1 ):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
                main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break
        """ 
        main.log.info( "Uninstalling ONOS" )
        for node in main.nodes:
            main.ONOSbench.onosUninstall( node.ip_address )

        # Make sure ONOS process is not running
        main.log.info( "Killing any ONOS processes" )
        killResults = main.TRUE
        for node in main.nodes:
            killed = main.ONOSbench.onosKill( node.ip_address )
            killResults = killResults and killed

        cleanInstallResult = main.TRUE
        gitPullResult = main.TRUE
        main.step( "Git checkout and pull" + gitBranch )
        if PULLCODE:
            main.ONOSbench.gitCheckout( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()
            # values of 1 or 3 are good
            utilities.assert_lesser( expect=0, actual=gitPullResult,
                                      onpass="Git pull successful",
                                      onfail="Git pull failed" )

        main.ONOSbench.getVersion( report=True )

        main.step( "Using mvn clean install" )
        cleanInstallResult = main.TRUE
        if PULLCODE and gitPullResult == main.TRUE:
            cleanInstallResult = main.ONOSbench.cleanInstall()
        else:
            main.log.warn( "Did not pull new code so skipping mvn" +
                           "clean install" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cleanInstallResult,
                                 onpass="MCI successful",
                                 onfail="MCI failed" )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        utilities.assert_equals( expect=main.TRUE,
                                     actual=packageResult,
                                     onpass="Successfully created ONOS package",
                                     onfail="Failed to create ONOS package" )

        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall(
                options="-f", node=main.nodes[0].ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=onosInstallResult,
                                 onpass="ONOS install successful",
                                 onfail="ONOS install failed" )
         
        main.step( "Checking if ONOS is up yet" )
        print main.nodes[0].ip_address
        for i in range( 2 ):
            onos1Isup = main.ONOSbench.isup( main.nodes[0].ip_address )
            if onos1Isup:
                break
        utilities.assert_equals( expect=main.TRUE, actual=onos1Isup,
                                 onpass="ONOS startup successful",
                                 onfail="ONOS startup failed" )
        main.log.step( "Starting ONOS CLI sessions" )
        print main.nodes[0].ip_address
        cliResults = main.ONOScli1.startOnosCli( main.nodes[0].ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS cli startup successful",
                                 onfail="ONOS cli startup failed" )
        
        main.step( "App Ids check" )
        appCheck = main.ONOScli1.appToIDCheck()

        if appCheck !=main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )
            utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )
        if cliResults == main.FALSE:
            main.log.error( "Failed to start ONOS,stopping test" )
            main.cleanup()
            main.exit()

        main.step( "Install onos-ovsdatabase" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.ovsdb" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-ovsdatabase successful",
                                 onfail="Install onos-ovsdatabase failed" )
        
        main.step( "Install onos-app-vtnrsc" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.vtnrsc" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-vtnrsc successful",
                                 onfail="Install onos-app-vtnrsc failed" )
        
        main.step( "Install onos-app-vtn" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.vtn" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-vtn successful",
                                 onfail="Install onos-app-vtn failed" )
        
        main.step( "Install onos-app-vtnweb" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.vtnweb" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-vtnweb successful",
                                 onfail="Install onos-app-vtnweb failed" )
        """
    def CASE2( self, main ):
        """
        Configure Network Subnet Port
        """
        import os

        try:
            from tests.FUNCovsdbtestL3.dependencies.Nbdata import NetworkData
            from tests.FUNCovsdbtestL3.dependencies.Nbdata import SubnetData
            from tests.FUNCovsdbtestL3.dependencies.Nbdata import VirtualPortData
            from tests.FUNCovsdbtestL3.dependencies.Nbdata import RouterData
            from tests.FUNCovsdbtestL3.dependencies.Nbdata import RouterInterfaceData
            from tests.FUNCovsdbtestL3.dependencies.Nbdata import FloatingIpData
            
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "Configure Network Subnet Port Start" )
        main.case( "Configure Network Subnet Port" )
        main.caseExplanation = "Configure Network Subnet Port " +\
                                "Verify post is OK"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.step( "Generate Post Data of Inner Network" )
        network = NetworkData()
        network.id = '1000000000000002'
        network.tenant_id = '1000000000000001'      
        subnet1 = SubnetData()
        subnet1.id = "1000000000000003"
        subnet1.tenant_id = network.tenant_id
        subnet1.network_id = network.id
        subnet1.gateway_ip = '192.168.33.254'
        subnet1.start = "192.168.33.1"
        subnet1.end = "192.168.33.254"
        subnet1.cidr = "192.168.33.0/24"
        subnet2 = SubnetData()
        subnet2.id = "1000000000000004"
        subnet2.tenant_id = network.tenant_id
        subnet2.network_id = network.id
        subnet2.gateway_ip = '192.168.44.254'
        subnet2.start = "192.168.44.1"
        subnet2.end = "192.168.44.254"
        subnet2.cidr = "192.168.44.0/24"
        
        port1 = VirtualPortData()
        port1.id = "00000000-0000-0000-0000-000000000001"
        port1.subnet_id = subnet1.id
        port1.tenant_id = network.tenant_id
        port1.network_id = network.id
        port1.macAddress = "00:00:00:00:00:01"
        port1.ip_address = "192.168.33.1"
        port2 = VirtualPortData()
        port2.id = "00000000-0000-0000-0000-000000000002"
        port2.subnet_id = subnet2.id
        port2.tenant_id = network.tenant_id
        port2.network_id = network.id
        port2.macAddress = "00:00:00:00:00:02"
        port2.ip_address = "192.168.44.1"
        """ 
        main.step("Generate Post Data of Ext Network")
        exnetwork = NetworkData()
        exnetwork.id = '1000000000000011'
        exnetwork.tenant_id = '1000000000000001'
        exsubnet = SubnetData()
        exsubnet.id = "1000000000000012"
        exsubnet.tenant_id = exnetwork.tenant_id
        exsubnet.network_id = exnetwork.id
        exsubnet.gateway_ip = '192.168.22.254'
        gwport = VirtualPortData()
        gwport.id = "00000000-0000-0000-0000-000000000003"
        gwport.subnet_id = exsubnet.id
        gwport.tenant_id = exnetwork.tenant_id
        gwport.network_id = exnetwork.id
        gwport.macAddress = "00:00:00:00:00:03"
        gwport.device_id = '1000000000000010'
        """
        router = RouterData()
        router.id = '1000000000000010'
        router.network_id = network.id
        router.tenant_id = network.tenant_id
        #router.subnet_id = exsubnet.id
        #router.ip_address = '192.168.22.33'
        #router.gw_port_id = gwport.id
         
        main.step("Generate Post Data of Inner RouteInterface")
        riport1 = VirtualPortData()
        riport1.state = 'DOWN'
        riport1.id = "00000000-0000-0000-0000-000000000004"
        riport1.subnet_id = subnet1.id
        riport1.tenant_id = network.tenant_id
        riport1.network_id = network.id
        riport1.ip_address = '192.168.33.254'
        riport1.macAddress = "00:00:00:00:00:04"
        riport1.deviceId = router.id
        riport2 = VirtualPortData()
        riport2.state = 'DOWN'
        riport2.id = "00000000-0000-0000-0000-000000000005"
        riport2.subnet_id = subnet2.id
        riport2.tenant_id = network.tenant_id
        riport2.network_id = network.id
        riport2.ip_address = '192.168.44.254'
        riport2.macAddress = "00:00:00:00:00:05"
        riport2.deviceId = router.id
        routerinterface1 = RouterInterfaceData()
        routerinterface1.id = riport1.deviceId
        routerinterface1.subnet_id = riport1.subnet_id
        routerinterface1.tenant_id = riport1.tenant_id
        routerinterface1.port_id = riport1.id
        routerinterface2 = RouterInterfaceData()
        routerinterface2.id = riport2.deviceId
        routerinterface2.subnet_id = riport2.subnet_id
        routerinterface2.tenant_id = riport2.tenant_id
        routerinterface2.port_id = riport2.id
        """ 
        main.step("Generate Post Data of Inner FloatingIp")
        flport = VirtualPortData()
        flport.id = "9352e05c-58b8-4f2c-b4df-c20435ser56466"
        flport.subnet_id = subnet1.id
        flport.tenant_id = network.tenant_id
        flport.network_id = network.id
        flport.device_Id = '91a546ea-8add-47e7-ad98-15677c74b337'
        flport.macAddress = "00:00:00:00:00:06"
        floatingip = FloatingIpData()
        floatingip.id = flport.device_Id
        floatingip.floating_network_id = flport.network_id
        floatingip.tenant_id = router.tenant_id
        floatingip.floating_ip_address = '192.168.22.4'
        floatingip.router_id = router.id
        floatingip.port_id = flport.id
        floatingip.fixed_ip_address = '10.0.0.1'
        """
        
        
        networkpostdata = network.DictoJson()
        subnet1postdata = subnet1.DictoJson()
        subnet2postdata = subnet2.DictoJson()
        port1postdata = port1.DictoJson()
        port2postdata = port2.DictoJson()
        #exnetworkpostdata = exnetwork.DictoJson()
        #exsubnetpostdata = exsubnet.DictoJson()
        #gwportpostdata = gwport.DictoJson()
        routerpostdata = router.DictoJson()
        riportpostdata1 = riport1.DictoJson()
        routerinterfacedata1 = routerinterface1.DictoJson()
        riportpostdata2 = riport2.DictoJson()
        routerinterfacedata2 = routerinterface2.DictoJson()
        #flportpostdata = flport.DictoJson()
        #floatingippostdata = floatingip.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet1 Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnet1postdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet1 Success",
                onfail="Post Subnet1 Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post Subnet2 Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnet2postdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet2 Success",
                onfail="Post Subnet2 Failed " + str( Poststatus ) + "," + str( result ) )        

        main.step( "Post Port1 Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, port1postdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port1 Success" + str(port1postdata),
                onfail="Post Port1 Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port2 Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, port2postdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port2 Success",
                onfail="Post Port2 Failed " + str( Poststatus ) + "," + str( result ) )
        """
        main.step( "Post ExNetwork Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, exnetworkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post ExNetwork Success",
                onfail="Post ExNetwork Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post ExSubnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, exsubnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post ExSubnet Success",
                onfail="Post ExSubnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post GwPort Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, gwportpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post GwPort Success",
                onfail="Post GwPort Failed " + str( Poststatus ) + "," + str( result ) )
        """ 
        main.step( "Post Router Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/',
                                                 'POST', None, routerpostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post Router Success",
                onfail="Post Router Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post RIPort1 Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, riportpostdata1 )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post RIPort1 Success",
                onfail="Post RIPort1 Failed " + str( Poststatus ) + "," + str( result ) )
                
        main.step( "Post RouterInterface1 Data via HTTP")
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/' +
                                                 router.id + '/add_router_interface/', 
                                                 'PUT', None, routerinterfacedata1 )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post RouterInterface1 Success",
                onfail="Post RouterInterface1 Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post RIPort2 Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, riportpostdata2 )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post RIPort2 Success",
                onfail="Post RIPort2 Failed " + str( Poststatus ) + "," + str( result ) )
                
        main.step( "Post RouterInterface2 Data via HTTP")
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'routers/' +
                                                 router.id + '/add_router_interface/', 
                                                 'PUT', None, routerinterfacedata2 )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post RouterInterface2 Success",
                onfail="Post RouterInterface2 Failed " + str( Poststatus ) + "," + str( result ) )        
        """ 
        main.step( "Post FLPort Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, flportpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post FLPort Success",
                onfail="Post FLPort Failed " + str( Poststatus ) + "," + str( result ) )
        
        main.step( "Post FloatingIp Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'floatingips/',
                                                 'POST', None, floatingippostdata )
        utilities.assert_equals(
                expect='201',
                actual=Poststatus,
                onpass="Post FloatingIp Success",
                onfail="Post FloatingIp Failed " + str( Poststatus ) + "," + str( result ) )   
        """
    def CASE3( self, main ):

        """
        Test through East-West and South-North
        """
        import re
        import time
        import os,sys

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ovsdbport = main.params[ 'CTRL' ][ 'ovsdbport' ]
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]

        main.step( "ovsdb node 1 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB1.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 set ovs manager to  to " +\
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 1 set ovs manager to  to " +\
                                  str( ctrlip ) + " failed" )

        main.step( "ovsdb node 2 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB2.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 set ovs manager to " +\
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 2 set ovs manager to " +\
                                  str( ctrlip ) + " failed" )

        main.step( "Create host1 on node 1 " + str( OVSDB1Ip ) )
        stepResult = main.OVSDB1.createHost( hostname="host1" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Create host1 on node 1 " + str( OVSDB1Ip ) + " sucess",
                                 onfail="Create host1 on node 1 " + str( OVSDB1Ip ) + " failed" )

        main.step( "Create host2 on node 2 " + str( OVSDB2Ip ) )
        stepResult = main.OVSDB2.createHost( hostname="host2" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Create host2 on node 2 " + str( OVSDB2Ip ) + " sucess",
                                 onfail="Create host2 on node 2 " + str( OVSDB2Ip ) + " failed" )

        main.step( "Create port on host1 on the node " + str ( OVSDB1Ip ) )
        stepResult = main.OVSDB1.createHostport( hostname="host1", hostport="host1-eth0", hostportmac="000000000001" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Create port on host1 on the node " + str( OVSDB1Ip ) + " sucess",
                                 onfail="Create port on host1 on the node " + str( OVSDB1Ip ) + " failed" )

        main.step( "Create port on host2 on the node " + str ( OVSDB2Ip ) )
        stepResult = main.OVSDB2.createHostport( hostname="host2", hostport="host2-eth0", hostportmac="000000000002" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Create port on host1 on the node " + str( OVSDB2Ip ) + " sucess",
                                 onfail="Create port on host1 on the node " + str( OVSDB2Ip ) + " failed" )
         
        main.step( "Add port to ovs br-int and host go-online on the node " + str ( OVSDB1Ip ) )
        stepResult = main.OVSDB1.addPortToOvs( ovsname="br-int", ifaceId="00000000-0000-0000-0000-000000000001",
                                               attachedMac="00:00:00:00:00:01", vmuuid="10000000-0000-0000-0000-000000000001" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Add port to ovs br-int and host go-online on the node " +\
                                  str( OVSDB1Ip ) + " sucess",
                                 onfail="Add port to ovs br-int and host go-online on the node " +\
                                  str( OVSDB1Ip ) + " failed" )
        
        time.sleep(10)  
        main.step( "Add port to ovs br-int and host go-online on the node " + str ( OVSDB2Ip ) )
        stepResult = main.OVSDB2.addPortToOvs( ovsname="br-int", ifaceId="00000000-0000-0000-0000-000000000002",
                                               attachedMac="00:00:00:00:00:02", vmuuid="10000000-0000-0000-0000-000000000002" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Add port to ovs br-int and host go-online on the node " +\
                                  str( OVSDB2Ip ) + " sucess",
                                 onfail="Add port to ovs br-int and host go-online on the node " +\
                                  str( OVSDB2Ip ) + " failed" )
        
        main.step( "Check onos set host flows on the node " + str( OVSDB1Ip ) )
        response = main.OVSDB1.dumpFlows( sw="br-int", protocols="OpenFlow13" )
        if re.search( "00:00:00:00:00:01", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check onos set host flows on the node " +\
                                  str( OVSDB1Ip ) + " sucess",
                                 onfail="Check onos set host flows on the node " +\
                                  str( OVSDB1Ip ) + " failed" )

        main.step( "Check onos set host flows on the node " + str( OVSDB2Ip ) )
        response = main.OVSDB2.dumpFlows( sw="br-int", protocols="OpenFlow13" )
        if re.search( "00:00:00:00:00:02", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check onos set host flows on the node " +\
                                  str( OVSDB2Ip ) + " sucess",
                                 onfail="Check onos set host flows on the node " +\
                                  str( OVSDB2Ip ) + " failed" )
        
        main.step( "Check hosts can ping each other" )
        main.OVSDB1.setHostportIp( hostname="host1", hostport1="host1-eth0", ip="192.168.33.1/24" )
        
        main.OVSDB2.setHostportIp( hostname="host2", hostport1="host2-eth0", ip="192.168.44.1/24" )
        main.OVSDB1.setHostportGateway( hostname="host1", gateway="192.168.33.254" )
        main.OVSDB2.setHostportGateway( hostname="host2", gateway="192.168.44.254" ) 
        time.sleep(10) 
        pingResult1 = main.OVSDB1.hostPing( src="192.168.33.1", hostname="host1", target="192.168.44.1" )
        pingResult2 = main.OVSDB2.hostPing( src="192.168.44.1", hostname="host2", target="192.168.33.1" )
        stepResult = pingResult1 and pingResult2
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully host go online and ping each other,controller is " +\
                                        str( ctrlip ),
                                 onfail="Failed to host go online and ping each other,controller is " +\
                                        str( ctrlip ) )
        """ 
        main.step( "Check hosts can ping baidu" )
        #main.OVSDB1.setHostportIp( hostname="host1", hostport1="host1-eth0", ip="10.0.0.1" )
        pingResult1 = main.OVSDB1.hostPing( src="10.0.0.1", hostname="host1", target="14.215.177.38" )
        stepResult = pingResult1
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully host go online and ping baidu,controller is " +\
                                        str( ctrlip ),
                                 onfail="Failed to host go online and ping baidu,controller is " +\
                                        str( ctrlip ) )
        """ 
    def CASE4( self, main ):

        """
        Clear ovs configuration and host configuration
        """
        import re
        import time
        import os,sys

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        OVSDB1Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip1' ] )
        OVSDB2Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip2' ] )
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]


        main.step( "Delete ip netns host on the ovsdb node 1" )
        deleteResult = main.OVSDB1.delHost( hostname="host1" )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Delete ip netns host on the ovsdb node 1 sucess",
                                 onfail="Delete ip netns host on the ovsdb node 1 failed" )

        main.step( "Delete ip netns host on the ovsdb node 2" )
        deleteResult = main.OVSDB2.delHost( hostname="host2" )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Delete ip netns host on the ovsdb node 2 sucess",
                                 onfail="Delete ip netns host on the ovsdb node 2 failed" )

        main.step( "Delete ovsdb node 1 bridge br-int" )
        deleteResult = main.OVSDB1.delBr( sw="br-int" )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Delete ovsdb node 1 bridge br-int sucess",
                                 onfail="Delete ovsdb node 1 bridge br-int failed" )

        main.step( "Delete ovsdb node 2 bridge br-int" )
        deleteResult = main.OVSDB2.delBr( sw="br-int" )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Delete ovsdb node 2 bridge br-int sucess",
                                 onfail="Delete ovsdb node 2 bridge br-int failed" )

        main.step( "Delete ovsdb node 1 manager" )
        deleteResult = main.OVSDB1.delManager( delaytime=delaytime )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 delete manager sucess",
                                 onfail="ovsdb node 1 delete manager failed" )

        main.step( "Delete ovsdb node 2 manager" )
        deleteResult = main.OVSDB2.delManager( delaytime=delaytime )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 delete manager sucess",
                                 onfail="ovsdb node 2 delete manager failed" )

        """
        main.step( "Check onoscli devices openflow session is false " + str( OVSDB1Ip ) )
        response = main.ONOScli1.devices()
        if re.search( OVSDB1Ip, response ) and not re.search( "true", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check openflow session is false " + str( OVSDB1Ip ) + " sucess",
                                 onfail="Check openflow session is false " + str( OVSDB1Ip ) + " failed" )

        main.step( "Check onoscli devices have ovs " + str( OVSDB2Ip ) )
        response = main.ONOScli1.devices()
        if re.search( OVSDB2Ip, response ) and not re.search( "true", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check openflow session is false " + str( OVSDB2Ip ) + " sucess",
                                 onfail="Check openflow session is false " + str( OVSDB2Ip ) + " failed" )
        """
