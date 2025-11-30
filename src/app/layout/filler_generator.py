#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filler Component Generation Module
"""

from typing import List
from .voltage_domain import VoltageDomainHandler

class FillerGenerator:
    """Filler Component Generator"""
    
    @staticmethod
    def get_filler_type(component1: dict, component2: dict) -> str:
        """Determine filler type based on voltage domains of two components"""
        domain1 = VoltageDomainHandler.get_voltage_domain(component1)
        domain2 = VoltageDomainHandler.get_voltage_domain(component2)
        
        # If both components are digital domain
        if domain1 == "digital" and domain2 == "digital":
            # Check if they are the same digital domain
            if VoltageDomainHandler.is_same_voltage_domain(component1, component2):
                return "PFILLER20_G"
            else:
                # Isolation needed between different digital domains
                return "PRCUTA_G"
        
        # If both components are analog domain
        if domain1 == "analog" and domain2 == "analog":
            # Check if they are the same analog domain
            if VoltageDomainHandler.is_same_voltage_domain(component1, component2):
                return "PFILLER20A_G"
            else:
                # Isolation needed between different analog domains
                return "PRCUTA_G"
        
        # Isolation needed between digital and analog domains
        if (domain1 == "digital" and domain2 == "analog") or (domain1 == "analog" and domain2 == "digital"):
            return "PRCUTA_G"
        
        # Default case
        return "PFILLER20_G"
    
    @staticmethod
    def get_filler_type_for_corner_and_pad(corner_type: str, pad1: dict, pad2: dict = None) -> str:
        """Determine filler type for corner and pad, simplified logic: if adjacent pads are different, insert PRCUTA_G between corner and pad"""
        
        # If only one pad parameter (backward compatibility), use PRCUTA_G directly
        if pad2 is None:
            return "PRCUTA_G"
        
        # Check if two pads belong to different voltage domains
        domain1 = VoltageDomainHandler.get_voltage_domain(pad1)
        domain2 = VoltageDomainHandler.get_voltage_domain(pad2)
        
        # If two pads belong to different voltage domains, use separator
        if domain1 != domain2:
            return "PRCUTA_G"
        
        # If two pads belong to the same voltage domain, choose filler based on voltage domain type
        if domain1 == "digital":
            return "PFILLER20_G"
        elif domain1 == "analog":
            return "PFILLER20A_G"
        else:
            # Default case
            return "PFILLER20_G"
    
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