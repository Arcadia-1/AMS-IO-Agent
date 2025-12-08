procedure(getDeviceTemplate(libName cellName viewName)
  let((schView pcellMaster tempInst)
    schView = dbOpenCellViewByType("yian_" "L0_IO_RING" "schematic" "schematic" "w")
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

getDeviceTemplate("tpd018bcdnv5" "PVSS2CDG" "symbol")
getDeviceTemplate("tpd018bcdnv5" "PVDD2CDG" "symbol")
getDeviceTemplate("tpd018bcdnv5" "PVSS1CDG" "symbol")
getDeviceTemplate("tpd018bcdnv5" "PVDD1CDG" "symbol")
getDeviceTemplate("tpd018bcdnv5" "PVDD1ANA" "symbol")
getDeviceTemplate("tpd018bcdnv5" "PVSS1ANA" "symbol")
getDeviceTemplate("tpd018bcdnv5" "PDDW0412SCDG" "symbol")

printf("Batch template extraction completed!\n")
t

