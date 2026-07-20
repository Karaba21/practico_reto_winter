Feature: Operación Frazadita - Compra de productos de invierno
  Como usuario de la tienda online Geant
  Quiero buscar y agregar productos de invierno al carrito
  Para poder validar que el carrito refleje los ítems y el total correctos

  Scenario: Buscar dos productos de invierno, agregarlos al carrito y validar el total
    Given que ingreso a la tienda online de Geant
    When busco "manta" y agrego el primer resultado al carrito
    And busco "calefactor" y agrego el primer resultado al carrito
    And voy al carrito
    Then el carrito debe contener 2 productos distintos
    And el total del carrito debe ser igual a la suma de los precios de los productos agregados
    And capturo una captura de pantalla del detalle del carrito
