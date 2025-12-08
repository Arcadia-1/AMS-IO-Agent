procedure(getDeviceTemplate(libName cellName viewName)
  let((schView pcellMaster tempInst)
    schView = dbOpenCellViewByType("LLM_Layout_Design" "test_v2" "schematic" "schematic" "w")
    pcellMaster = dbOpenCellView(libName cellName viewName)
    
    when(pcellMaster
      printf("DEVICE_INFO: %s,%s,%s\n" libName cellName viewName)
      
      tempInst = dbCreateInst(schView pcellMaster "TEMP" '(0 0) "R0")
      
      when(tempInst
        instBBox = tempInst~>bBox
        if(instBBox then
          instCenterX = (car(car(instBBox)) + car(cadr(instBBox))) / 2.0
          instCenterY = (cadr(car(instBBox)) + cadr(cadr(instBBox))) / 2.0
          printf("DEVICE_CENTER: %.3f,%.3f\n" instCenterX instCenterY)
        else
          instCenterX = 0.0
          instCenterY = 0.0
          printf("DEVICE_CENTER: 0.000,0.000\n")
        )
        
        foreach(masterTerm pcellMaster~>terminals
          foreach(pin masterTerm~>pins
            pinLoc = centerBox(pin~>fig~>bBox)
            when(pinLoc
              pinX = car(pinLoc)
              pinY = cadr(pinLoc)
              
              deltaY = pinY - instCenterY
              
              if(deltaY > 0 then
                side = "top"
              else
                side = "bottom"
              )
              
              printf("PIN_TEMPLATE: %s,%.3f,%.3f,%s\n" 
                masterTerm~>name pinX pinY side)
            )
          )
        )
        
        dbDeleteObject(tempInst)
      )
      
      printf("TEMPLATE_END\n")
    )
  )
)

printf("Starting batch template extraction (top/bottom only)...\n")

getDeviceTemplate("tphn28hpcpgv18" "PDB3AC_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PDB3AC_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD1AC_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD1AC_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS1AC_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS1AC_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD3A_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD3A_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS3A_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS3A_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD3AC_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD3AC_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS3AC_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS3AC_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PDDW16SDGZ_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PDDW16SDGZ_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD1DGZ_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD1DGZ_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS1DGZ_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS1DGZ_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD2POC_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVDD2POC_H_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS2DGZ_V_G" "symbol")
getDeviceTemplate("tphn28hpcpgv18" "PVSS2DGZ_H_G" "symbol")

printf("Batch template extraction completed!\n")
t

