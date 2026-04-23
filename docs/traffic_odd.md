# 1. Purpose Patterns

Wir wollen wissen warum und unter welchen Bedingungen Phantom staus entstehen.

Rückwärts laufende Stauwelle
Spontane Staubildung
Stabile Staucluster

# 2. Entities, State Variables, Scales

Fahrzeuge:
- Geschwindigkeit
- Position
  
Straße 230m
Anzahl Fahrzeuge 22
Sicherheitsabstand 10m
Maximalgeschwindigkeit (Zielgeschwindigkeit) 30kmh
Simulationsdauer 300s
Zeitschritt Dauer 0.01s

# 4. Design Concepts

Stochasticity:
Fahrzeuge fahren zufällig plötzlich langsamer (menschliche variabilität)

# 5. Initialisierung

22 Fahrzeuge, gleichmäßig Verteilt

# 7. 

Fahrverhalten

Wenn Abstand < Sicherheitsabstand -> plötzlich abbremsen  v = 0
Wenn Abstand > Sicherheitsabstand und Geschwindigkeit < v_max -> Beschleunigen => v += 3
Wenn Abstand > Sicherheitsabstand und Geschwindigkeit = v_max -> keine Veränderung

position Veränderung abhängig von Geschwindigkeit und Zeitschrittlänge
