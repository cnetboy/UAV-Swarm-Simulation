#ifdef NS3_MODULE_COMPILATION 
    error "Do not include ns3 module aggregator headers from other modules these are meant only for end user scripts." 
#endif 
#ifndef NS3_MODULE_UAV_SIM_FRAMEWORK
    // Module headers: 
    #include <ns3/uav-sim-types.h>
    #include <ns3/simulation-plugin.h>
    #include <ns3/simulation-context.h>
    #include <ns3/plugin-registry.h>
    #include <ns3/data-exporter.h>
    #include <ns3/mobility-plugin.h>
    #include <ns3/channel-plugin.h>
    #include <ns3/traffic-plugin.h>
    #include <ns3/collector-plugin.h>
    #include <ns3/uav-sim-helper.h>
#endif 