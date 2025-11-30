#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voltage Domain Processing Module
"""

from .device_classifier import DeviceClassifier

class VoltageDomainHandler:
    """Voltage Domain Handler"""
    
    @staticmethod
    def get_voltage_domain(component: dict) -> str:
        """Get the voltage domain type of the component (digital or analog)"""
        # If the component has pin_connection, determine from pin_connection
        if "pin_connection" in component:
            pin_connection = component["pin_connection"]
            
            # Check if it contains digital domain related pins
            digital_pins = ["VDD", "VSS", "VDDPST", "VSSPST"]
            analog_pins = ["TACVDD", "TACVSS", "TAVDD", "TAVSS"]
            
            has_digital = any(pin in pin_connection for pin in digital_pins)
            has_analog = any(pin in pin_connection for pin in analog_pins)
            
            if has_digital and not has_analog:
                return "digital"
            elif has_analog:
                return "analog"
            else:
                return "unknown"
        
        # If the component has voltage domain configuration, use it directly (backward compatibility)
        if "voltage_domain" in component:
            voltage_domain = component["voltage_domain"]
            
            # Check if it's a digital domain configuration (contains digital_domain field)
            if "digital_domain" in voltage_domain:
                return "digital"
            
            # Old format compatibility
            power = voltage_domain.get("power", "")
            ground = voltage_domain.get("ground", "")
            
            # Determine type based on voltage domain name
            if "DIG" in power or "DIG" in ground:
                return "digital"
            elif "AC" in power or "AC" in ground or "A" in power or "A" in ground or "IB" in power or "IB" in ground or "CKB" in power or "CKB" in ground:
                return "analog"
            else:
                return "unknown"
        
        # If no configuration, use device type to determine (backward compatibility)
        device = component.get("device", "")
        
        # Digital voltage domain
        digital_devices = [
            "PDDW16SDGZ_V_G", "PDDW16SDGZ_H_G", "PDDW16SDGZ",
            "PVDD1DGZ_V_G", "PVDD1DGZ_H_G",
            "PVSS1DGZ_V_G", "PVSS1DGZ_H_G",
            "PVDD2POC_V_G", "PVDD2POC_H_G", "PVDD2POC",
            "PVSS2DGZ_V_G", "PVSS2DGZ_H_G", "PVSS2DGZ",
            "PCORNER_G"  # Digital corner
        ]
        
        # Analog voltage domain
        analog_devices = [
            "PDB3AC_V_G", "PDB3AC_H_G", "PDB3AC",
            "PVDD1AC_V_G", "PVDD1AC_H_G", "PVDD1AC",
            "PVSS1AC_V_G", "PVSS1AC_H_G", "PVSS1AC",
            "PVDD3A_V_G", "PVDD3A_H_G",
            "PVSS3A_V_G", "PVSS3A_H_G",
            "PVDD3AC_V_G", "PVDD3AC_H_G",
            "PVSS3AC_V_G", "PVSS3AC_H_G",
            "PCORNERA_G"  # Analog corner
        ]
        
        if device in digital_devices:
            return "digital"
        elif device in analog_devices:
            return "analog"
        else:
            return "unknown"
    
    @staticmethod
    def get_voltage_domain_key(component: dict) -> str:
        """Get the voltage domain key of the component, used to determine if it's the same voltage domain"""
        # If the component has pin_connection, determine from pin_connection
        if "pin_connection" in component:
            pin_connection = component["pin_connection"]
            
            # Check digital domain related pins
            digital_pins = ["VDD", "VSS", "VDDPST", "VSSPST"]
            analog_pins = ["TACVDD", "TACVSS", "TAVDD", "TAVSS"]
            
            has_digital = any(pin in pin_connection for pin in digital_pins)
            has_analog = any(pin in pin_connection for pin in analog_pins)
            
            if has_digital and not has_analog:
                # Digital domain, determine based on VDD/VSS label
                vdd_label = pin_connection.get("VDD", {}).get("label", "")
                vss_label = pin_connection.get("VSS", {}).get("label", "")
                return f"DIGITAL_{vdd_label}_{vss_label}"
            elif has_analog:
                # Analog domain, determine based on TACVDD/TACVSS label
                tacvdd_label = pin_connection.get("TACVDD", {}).get("label", "")
                tacvss_label = pin_connection.get("TACVSS", {}).get("label", "")
                if not tacvdd_label:
                    tacvdd_label = pin_connection.get("TAVDD", {}).get("label", "")
                if not tacvss_label:
                    tacvss_label = pin_connection.get("TAVSS", {}).get("label", "")
                return f"ANALOG_{tacvdd_label}_{tacvss_label}"
            else:
                return "unknown"
        
        # If the component has voltage domain configuration, use it directly (backward compatibility)
        if "voltage_domain" in component:
            voltage_domain = component["voltage_domain"]
            
            # If both are digital domain configurations, compare digital_domain
            if "digital_domain" in voltage_domain:
                return voltage_domain["digital_domain"]
            
            # If both are analog domain configurations, compare power and ground
            if "power" in voltage_domain and "ground" in voltage_domain:
                return f"{voltage_domain['power']}_{voltage_domain['ground']}"
        
        # If no configuration, use device type to determine (backward compatibility)
        device = component.get("device", "")
        
        # Define device type to voltage domain mapping
        device_to_voltage_domain = {
            # Digital domain devices - determine digital domain based on device type
            "PDDW16SDGZ_V_G": "DIGITAL_IO",  # Digital IO domain
            "PDDW16SDGZ_H_G": "DIGITAL_IO",
            "PDDW16SDGZ": "DIGITAL_IO",
            "PVDD1DGZ_V_G": "DIGITAL_1",     # Digital domain 1
            "PVDD1DGZ_H_G": "DIGITAL_1",
            "PVSS1DGZ_V_G": "DIGITAL_1",
            "PVSS1DGZ_H_G": "DIGITAL_1",
            "PVDD2POC_V_G": "DIGITAL_2",     # Digital domain 2
            "PVDD2POC_H_G": "DIGITAL_2",
            "PVDD2POC": "DIGITAL_2",
            "PVSS2DGZ_V_G": "DIGITAL_2",
            "PVSS2DGZ_H_G": "DIGITAL_2",
            "PVSS2DGZ": "DIGITAL_2",
            
            # Analog domain devices
            "PDB3AC_V_G": "VDD3AC_VSS3AC",
            "PDB3AC_H_G": "VDD3AC_VSS3AC",
            "PDB3AC": "VDD3AC_VSS3AC",
            "PVDD1AC_V_G": "VDD1AC_VSS1AC",
            "PVDD1AC_H_G": "VDD1AC_VSS1AC",
            "PVDD1AC": "VDD1AC_VSS1AC",
            "PVSS1AC_V_G": "VDD1AC_VSS1AC",
            "PVSS1AC_H_G": "VDD1AC_VSS1AC",
            "PVSS1AC": "VDD1AC_VSS1AC",
            "PVDD3A_V_G": "VDD3A_VSS3A",
            "PVDD3A_H_G": "VDD3A_VSS3A",
            "PVSS3A_V_G": "VDD3A_VSS3A",
            "PVSS3A_H_G": "VDD3A_VSS3A",
            "PVDD3AC_V_G": "VDD3AC_VSS3AC",
            "PVDD3AC_H_G": "VDD3AC_VSS3AC",
            "PVSS3AC_V_G": "VDD3AC_VSS3AC",
            "PVSS3AC_H_G": "VDD3AC_VSS3AC",
        }
        
        return device_to_voltage_domain.get(device, "unknown")
    
    @staticmethod
    def is_same_digital_domain(component1: dict, component2: dict) -> bool:
        """Determine if two components belong to the same digital domain (high and low voltage belong to the same digital domain)"""
        domain_key1 = VoltageDomainHandler.get_voltage_domain_key(component1)
        domain_key2 = VoltageDomainHandler.get_voltage_domain_key(component2)
        
        # If both are digital domains, check if they are the same digital domain
        if domain_key1.startswith("DIGITAL_") and domain_key2.startswith("DIGITAL_"):
            return domain_key1 == domain_key2
        
        return False
    
    @staticmethod
    def is_same_voltage_domain(component1: dict, component2: dict) -> bool:
        """Determine if two components belong to the same voltage domain"""
        # Use get_voltage_domain_key to get the voltage domain key for comparison
        key1 = VoltageDomainHandler.get_voltage_domain_key(component1)
        key2 = VoltageDomainHandler.get_voltage_domain_key(component2)
        
        # If the two key values are the same and not unknown, they belong to the same voltage domain
        if key1 == key2 and key1 != "unknown":
            return True
        
        # Backward compatibility: if both components have voltage domain configuration, compare directly
        if "voltage_domain" in component1 and "voltage_domain" in component2:
            vd1 = component1["voltage_domain"]
            vd2 = component2["voltage_domain"]
            
            # If both are digital domain configurations, compare digital_domain
            if "digital_domain" in vd1 and "digital_domain" in vd2:
                return vd1["digital_domain"] == vd2["digital_domain"]
            
            # If both are analog domain configurations, compare power and ground
            if "power" in vd1 and "ground" in vd1 and "power" in vd2 and "ground" in vd2:
                return vd1["power"] == vd2["power"] and vd1["ground"] == vd2["ground"]
        
        return False
    
    @staticmethod
    def is_voltage_domain_provider(component: dict) -> bool:
        """Determine if the component is a voltage domain provider"""
        device = component.get("device", "")
        
        # Voltage domain provider device types
        provider_devices = [
            # Analog voltage domain providers
            "PVDD3AC_V_G", "PVDD3AC_H_G",
            "PVSS3AC_V_G", "PVSS3AC_H_G", 
            "PVDD3A_V_G", "PVDD3A_H_G",
            "PVSS3A_V_G", "PVSS3A_H_G",
        ]
        
        return device in provider_devices
    
    @staticmethod
    def is_voltage_domain_user(component: dict) -> bool:
        """Determine if the component is a voltage domain user"""
        device = component.get("device", "")
        
        # Voltage domain user device types
        user_devices = [
            # Analog voltage domain users
            "PDB3AC_V_G", "PDB3AC_H_G",
            "PVDD1AC_V_G", "PVDD1AC_H_G",
            "PVSS1AC_V_G", "PVSS1AC_H_G",
            # Digital voltage domain users
            "PDDW16SDGZ_V_G", "PDDW16SDGZ_H_G"
        ]
        
        return device in user_devices 