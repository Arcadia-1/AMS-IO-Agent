#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filler Component Generation Module
Loads filler device names from process node configuration
"""

from typing import List, Optional
from .voltage_domain import VoltageDomainHandler
from .process_node_config import get_process_node_config

class FillerGenerator:
    """Filler Component Generator"""
    
    @staticmethod
    def _get_filler_devices(process_node: str = "T28") -> dict:
        """Get filler device names from configuration"""
        config = get_process_node_config(process_node)
        return config.get("filler_components", {
            "analog_20": "PFILLER20A_G",
            "digital_20": "PFILLER20_G",
            "separator": "PRCUTA_G"
        })
    
    @staticmethod
    def get_filler_type(component1: dict, component2: dict, process_node: str = "T28") -> str:
        """Determine filler type based on voltage domains of two components"""
        domain1 = VoltageDomainHandler.get_voltage_domain(component1)
        domain2 = VoltageDomainHandler.get_voltage_domain(component2)
        
        filler_devices = FillerGenerator._get_filler_devices(process_node)
        
        # If both components are digital domain
        if domain1 == "digital" and domain2 == "digital":
            # Check if they are the same digital domain
            if VoltageDomainHandler.is_same_voltage_domain(component1, component2):
                return filler_devices.get("digital_20", "PFILLER20_G")
            else:
                # Isolation needed between different digital domains
                return filler_devices.get("separator", "PRCUTA_G")
        
        # If both components are analog domain
        if domain1 == "analog" and domain2 == "analog":
            # Check if they are the same analog domain
            if VoltageDomainHandler.is_same_voltage_domain(component1, component2):
                return filler_devices.get("analog_20", "PFILLER20A_G")
            else:
                # Isolation needed between different analog domains
                return filler_devices.get("separator", "PRCUTA_G")
        
        # Isolation needed between digital and analog domains
        if (domain1 == "digital" and domain2 == "analog") or (domain1 == "analog" and domain2 == "digital"):
            return filler_devices.get("separator", "PRCUTA_G")
        
        # Default case
        return filler_devices.get("digital_20", "PFILLER20_G")
    
    @staticmethod
    def get_filler_type_for_corner_and_pad(corner_type: str, pad1: dict, pad2: dict = None, process_node: str = "T28") -> str:
        """Determine filler type for corner and pad.
        
        Logic:
        1. If corner's two adjacent pads belong to different voltage domains, use separator (PRCUTA_G)
        2. If corner and pad belong to different voltage domains, use separator
        3. Otherwise, use appropriate filler based on voltage domain type
        """
        
        filler_devices = FillerGenerator._get_filler_devices(process_node)
        separator = filler_devices.get("separator", "PRCUTA_G")
        
        # Create corner component to check its voltage domain
        corner_component = FillerGenerator.create_corner_component(corner_type)
        
        # If only one pad parameter (backward compatibility), check corner and pad
        if pad2 is None:
            # Check if corner and pad belong to different voltage domains
            if not VoltageDomainHandler.is_same_voltage_domain(corner_component, pad1):
                return separator
            # Use appropriate filler based on pad's voltage domain
            pad_domain = VoltageDomainHandler.get_voltage_domain(pad1)
            if pad_domain == "digital":
                return filler_devices.get("digital_20", "PFILLER20_G")
            elif pad_domain == "analog":
                return filler_devices.get("analog_20", "PFILLER20A_G")
            else:
                return separator
        
        # Check if two pads belong to different voltage domains
        domain1 = VoltageDomainHandler.get_voltage_domain(pad1)
        domain2 = VoltageDomainHandler.get_voltage_domain(pad2)
        
        # If two pads belong to different voltage domains, use separator
        # This handles the case where corner's two adjacent pads are in different voltage domains
        # In this case, corner cannot belong to both voltage domains, so separator is needed
        if domain1 != domain2:
            return separator
        
        # Check if the two pads belong to the same voltage domain
        pads_same_domain = VoltageDomainHandler.is_same_voltage_domain(pad1, pad2)
        
        if not pads_same_domain:
            # If pads don't belong to the same voltage domain (shouldn't happen here due to check above),
            # but if it does, use separator
            return separator
        
        # If two pads belong to the same voltage domain, check if corner is compatible
        # Special handling: if both pads are analog and belong to the same specific analog voltage domain,
        # and corner is a generic analog corner (PCORNERA_G), they should be considered compatible
        if domain1 == "analog" and corner_type == "PCORNERA_G":
            # Get voltage domain keys
            corner_key = VoltageDomainHandler.get_voltage_domain_key(corner_component)
            pad_key = VoltageDomainHandler.get_voltage_domain_key(pad1)
            
            # If corner is generic analog (VDD_ANALOG_VSS_ANALOG) and pad is specific analog (ANALOG_*),
            # and both pads are in the same voltage domain, they are compatible
            # The corner can be considered as belonging to the same voltage domain as the pads
            if corner_key == "VDD_ANALOG_VSS_ANALOG" and pad_key.startswith("ANALOG_"):
                # Pads are in the same voltage domain, so corner is compatible - use appropriate filler
                pass  # Continue to use appropriate filler below
            elif not VoltageDomainHandler.is_same_voltage_domain(corner_component, pad1):
                # Corner and pad are in different voltage domains, use separator
                return separator
        elif not VoltageDomainHandler.is_same_voltage_domain(corner_component, pad1):
            # For other cases, if corner and pad belong to different voltage domains, use separator
            return separator
        
        # If corner and pads all belong to the same voltage domain, choose filler based on voltage domain type
        if domain1 == "digital":
            return filler_devices.get("digital_20", "PFILLER20_G")
        elif domain1 == "analog":
            return filler_devices.get("analog_20", "PFILLER20A_G")
        else:
            # Default case
            return filler_devices.get("digital_20", "PFILLER20_G")
    
    @staticmethod
    def create_corner_component(corner_type: str, name: str = "corner", voltage_domain: dict = None) -> dict:
        """Create corner component configuration, ensuring it contains name and appropriate voltage_domain field"""
        d = {"name": name, "device": corner_type}
        if voltage_domain:
            d["voltage_domain"] = voltage_domain
        elif corner_type == "PCORNERA_G":
            d["voltage_domain"] = {"power": "VDD_ANALOG", "ground": "VSS_ANALOG"}
        elif corner_type == "PCORNER_G":
            d["voltage_domain"] = {"power": "VDD_DIGITAL", "ground": "VSS_DIGITAL"}
        return d 