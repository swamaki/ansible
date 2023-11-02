#!/usr/bin/env python3
import re


class FilterModule:
    @staticmethod
    def filters():
        return {
            "bgp_as_from_rt": FilterModule.bgp_as_from_rt,
            "ios_vrf_rt": FilterModule.ios_vrf_rt,
        }

    @staticmethod
    def bgp_as_from_rt(rt_list):
        bgp_as_list = []
        for my_rt in rt_list:
            rt_halves = my_rt.split(":")
            bgp_as_list.append(int(rt_halves[0]))
        return bgp_as_list

    @staticmethod
    def ios_vrf_rt(text):
        vrf_list = ["vrf" + s for s in text.split("vrf") if s]
        print(vrf_list)
        return_dict = {}
        for vrf in vrf_list:
            # Parse the VRF name from the definition line
            name_regex = re.compile(r"vrf\s+definition\s+(?P<name>\S+)")
            name_match = name_regex.search(vrf)
            sub_dict = {}
            vrf_dict = {name_match.group("name"): sub_dict}

            # Parse the RT imports into a list of strings
            rti_regex = re.compile(r"route-target\s+import\s+(?P<rti>\d+:\d+)")
            rti_matches = rti_regex.findall(vrf)
            rti_matches = list(set(rti_matches))  # remove duplicate RTs
            rti_matches.sort()
            sub_dict.update({"route_import": rti_matches})

            # Parse the RT exports into a list of strings
            rte_regex = re.compile(r"route-target\s+export\s+(?P<rte>\d+:\d+)")
            rte_matches = rte_regex.findall(vrf)
            rte_matches = list(set(rte_matches))  # remove duplicate RTs
            rte_matches.sort()
            sub_dict.update({"route_export": rte_matches})

            # Append dictionary to return list
            return_dict.update(vrf_dict)
        return return_dict

        """
        Imagine getting a text blob like the one shown below: 

            text = "vrf definition VRF_1\n description VRF_1 EXAMPLE\n rd 65000:1\n route-target export 65000:1\n route-target export 713:713\n route-target export 714:714\n route-target import 65000:1\n route-target import 711:711\n route-target import 712:712\nvrf definition VRF_2\n description VRF_2 EXAMPLE\n rd 65000:2\n route-target export 65000:2\n route-target export 717:717\n route-target export 718:718\n route-target import 65000:2\n route-target import 715:715\n route-target import 716:716"

        What I do first is break the big blob into smaller chunks one per VRF. Ideally,  
        I want a list of the VRF stanzas and I use a Python list comprehension combined with string splitting 
        to achieve that. 
            
            [
            'vrf definition VRF_1\n description VRF_1 EXAMPLE\n rd 65000:1\n route-target export 65000:1\n route-target 
            export 713:713\n route-target export 714:714\n route-target import 65000:1\n route-target import 711:711\n 
            route-target import 712:712\n',
            'vrf definition VRF_2\n description VRF_2 EXAMPLE\n rd 65000:2\n route-target export 65000:2\n route-target 
            export 717:717\n route-target export 718:718\n route-target import 65000:2\n route-target import 715:715\n 
            route-target import 716:716'
            ]
        
        Then I use iteration to step through each VRF stanza individually. The "name_regex" regex pattern is 
        being used to search the VRF stanza for the VRF name and if found is stored in dictionary form(ie vrf_dict) 
            
        Remember the structure we want is a dictionary indexed by VRF name with a list of route-targets underneath.
        Thus, I create a new dictionary based on this name, and an empty inner dictionary as the value(ie sub_dict). 
        This inner dictionary is populated next.  

            {'VRF_1': {}}
        
        The method for parsing import and export route targets is similar.
        You want to grab ("route-target\s+import\s+(?P<rti>\d+:\d+)"). we must match all occurrences of this line since  
        there could be several, and store them in a list. 

            route-target imports: ['65000:1', '711:711', '712:712'] and ['65000:2', '715:715', '716:716']
            sub_dict = {'route import': ['65000:1', '711:711', '712:712']}<>VRF1 and {'route import': ['65000:2', '715:715', '716:716']} <> VRF2
            and similar for route-target exports
        
        Once complete, we update the VRF specific dictionary entry with that data. The same actions occur for export route-targets. 
        Once all the data has been parsed, the VRF specific dictionary is stored by adding it to the main dictionary. 
        After all the VRFs have been processed. The main dictionary is returned. 
        
        This hierarchical structure is easily traversed later.

        {
        'VRF_1': {
            'route import': ['65000:1', '711:711', '712:712'],
            'route export': ['65000:1', '713:713', '714:714']
        },
        'VRF_2': {
            'route import': ['65000:2', '715:715', '716:716'],
            'route export': ['65000:2', '717:717', '718:718']
        }
        }

        """
