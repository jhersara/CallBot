# Diseño de Arquitectura del Algoritmo de Trading Inteligente

## 1. Introducción

Este documento detalla la arquitectura propuesta para el algoritmo de trading inteligente que replicará la estrategia ganadora del trader, incorporando un sistema de gestión de capital compuesto. El algoritmo se integrará en el proyecto `CallBot` existente, extendiendo sus funcionalidades actuales.

## 2. Estrategia Ganadora (Hipótesis Inicial)

Dado que la estrategia de trading específica no ha sido detallada más allá de la gestión de capital, se asumirá una estrategia basada en la **estructura del mercado (BOS/CHOCH)** y **niveles de Fibonacci**, complementada con **bloques de órdenes (Order Blocks)** y **zonas de liquidez (Liquidity Zones)**, ya que estos módulos existen en el proyecto `CallBot`.

### Componentes Clave de la Estrategia:

*   **Detección de Estructura de Mercado:** Utilización de `market_structure.py` para identificar `BOS` (Break of Structure) y `CHOCH` (Change of Character) para determinar la dirección de la tendencia y posibles reversiones.
*   **Niveles de Fibonacci:** Aplicación de `fibonacci.py` para identificar posibles zonas de retroceso o extensión para entradas y salidas.
*   **Bloques de Órdenes:** Uso de `order_blocks.py` para identificar zonas de alta probabilidad donde las instituciones han dejado órdenes pendientes.
*   **Zonas de Liquidez:** Integración de `liquidity.py` para identificar áreas donde se espera que se acumule liquidez, lo que puede influir en el movimiento del precio.
*   **Filtros Adicionales:** Consideración de `news_filter.py` y `session_filter.py` para evitar operar durante eventos de alta volatilidad o fuera de sesiones de trading óptimas.

## 3. Gestión de Capital Compuesto

El sistema de gestión de capital es fundamental para la estrategia, basándose en un riesgo del 1% del capital total por operación y un ajuste dinámico del tamaño del lote (lotaje) en función del balance actual.

### Modificaciones a `risk_manager.py`:

El módulo `risk_manager.py` actual ya proporciona las funciones `calculate_risk_amount` y `calculate_lot_size`. Se modificará para:

*   **Actualización Dinámica del Balance:** Asegurar que el `balance` utilizado para el cálculo del riesgo sea siempre el balance actual de la cuenta, reflejando las ganancias o pérdidas.
*   **Cálculo de Lotaje Preciso:** La función `calculate_lot_size` se ajustará para considerar el valor del pip y el stop loss en pips, garantizando que el 1% de riesgo se mantenga constante independientemente del tamaño de la cuenta.

## 4. Arquitectura del Algoritmo

La arquitectura se basará en una estructura modular, permitiendo la fácil extensión y mantenimiento. Los componentes principales serán:

*   **`main.py` (Orquestador):** Coordinará el flujo de ejecución, la conexión con el broker (MT5), la obtención de datos, la aplicación de la estrategia, la gestión de riesgo y la ejecución de órdenes.
*   **`mt5/connector.py` (Conector MT5):** Responsable de la conexión con MetaTrader 5, la obtención de datos de mercado (velas), la ejecución de órdenes y la recuperación de información de la cuenta.
*   **`core/market_analyzer.py` (NUEVO - Analizador de Mercado):** Este módulo integrará la lógica de `market_structure.py`, `fibonacci.py`, `order_blocks.py`, y `liquidity.py` para generar señales de trading basadas en la estrategia combinada. Será el cerebro de la estrategia.
*   **`core/strategy_executor.py` (NUEVO - Ejecutor de Estrategia):** Recibirá las señales del `market_analyzer.py` y, en conjunto con `risk_manager.py`, determinará el tamaño del lote y ejecutará las órdenes a través del `mt5/connector.py`.
*   **`core/risk_manager.py` (Gestor de Riesgo):** Modificado para la gestión de capital compuesto, como se describió anteriormente.
*   **`core/trade_manager.py` (Gestor de Operaciones):** Gestionará las operaciones abiertas, incluyendo el seguimiento de stop loss, take profit y posibles ajustes.
*   **`notifications/notifier.py` (Notificador):** Para enviar alertas sobre operaciones, cambios de balance, etc.
*   **`gui/dashboard.py` (NUEVO - Dashboard de Monitoreo):** Una interfaz para visualizar el rendimiento del bot, el balance, las operaciones abiertas y los parámetros de riesgo.

## 5. Flujo de Ejecución

1.  **Inicialización:** `main.py` se conecta a MT5 y obtiene la información inicial de la cuenta.
2.  **Bucle Principal:**
    a.  Obtención de datos de mercado en tiempo real (velas).
    b.  `market_analyzer.py` procesa los datos y genera señales de trading (compra/venta).
    c.  Si hay una señal, `strategy_executor.py` consulta a `risk_manager.py` para calcular el lotaje óptimo.
    d.  `strategy_executor.py` ejecuta la orden a través de `mt5/connector.py`.
    e.  `trade_manager.py` monitorea las operaciones abiertas.
    f.  `notifier.py` envía notificaciones relevantes.
3.  **Actualización del Balance:** El balance de la cuenta se actualiza después de cada operación cerrada para que `risk_manager.py` pueda recalcular el riesgo para la siguiente operación.

## 6. Próximos Pasos

*   Implementar el módulo `market_analyzer.py` para consolidar la lógica de la estrategia.
*   Implementar el módulo `strategy_executor.py` para la ejecución de órdenes.
*   Modificar `risk_manager.py` para asegurar la actualización dinámica del balance.
*   Desarrollar el `dashboard.py` para monitoreo.

Este diseño proporciona una base sólida para el desarrollo del algoritmo, permitiendo una implementación incremental y una fácil adaptación a medida que se refine la estrategia de trading.
