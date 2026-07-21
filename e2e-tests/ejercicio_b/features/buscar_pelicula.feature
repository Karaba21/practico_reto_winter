Feature: Búsqueda y validación de película invernal
  Como usuario encerrado por el frío
  Quiero buscar la película "Ice Age" en TMDB
  Para validar su director y calificación antes de verla

  Scenario: Validar director y calificación de Ice Age
    Given que el usuario ingresa a TMDB
    When busca la película "Ice Age"
    And selecciona el primer resultado de la búsqueda
    Then el director debe ser "Chris Wedge"
    And la calificación debe ser mayor a 7.0
    And se guarda una captura de pantalla como evidencia