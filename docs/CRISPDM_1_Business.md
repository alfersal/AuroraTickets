# **Business Understanding** {#business-understanding}


**Contexto de Aurora Tickets** Para ponernos en situación, Aurora Tickets es una plataforma de venta de entradas. El problema que tienen es que últimamente están recibiendo mucho tráfico en la web, pero la gente no termina de comprar (tienen una conversión muy baja). Además, la web les va lenta a ratos y tienen la sospecha de que hay bots o tráfico raro metiéndose en el servidor. Hasta ahora no tenían ninguna forma de medir esto bien, así que me han contratado para montarles una arquitectura de Big Data en AWS desde cero.

**Stakeholders (A quién le importa esto)**

* **Al equipo de Marketing:** Quieren saber qué eventos generan interés real y cuáles acaban en compra, para no tirar el dinero en campañas que no funcionan.  
* **Al equipo de Operaciones/Sistemas:** Necesitan ver si hay picos de tráfico raros para poder bloquear IPs de bots y que no se les caiga el servidor.  
* **A la Dirección:** Quieren ver el embudo de ventas (funnel) claro y directo para saber cuánto dinero entra.

**Mis Objetivos y KPIs** Para resolver esto, he definido tres KPIs (métricas clave) en los que basar mi arquitectura:

1. **Tasa de conversión del Funnel:** Voy a medir cuántas sesiones pasan de ver el detalle, a iniciar el pago, y finalmente a comprar.  
2. **Ratio Interés vs Ingresos:** Voy a cruzar las veces que la gente mira un evento con las compras reales que genera.  
3. **Detección de anomalías (Bots):** Voy a rastrear cuántas peticiones seguidas hace una misma IP a un mismo endpoint.

Con estas métricas, la empresa podrá tomar decisiones reales, como bloquear automáticamente IPs sospechosas o cambiar la publicidad de un evento que la gente mira mucho pero no compra.

## 