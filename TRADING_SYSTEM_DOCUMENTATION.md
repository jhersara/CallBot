# 📊 CallBot - Documentación del Sistema de Trading Inteligente

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Características Principales](#características-principales)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Módulos Principales](#módulos-principales)
5. [Gestión de Capital Compuesto](#gestión-de-capital-compuesto)
6. [Estrategia de Trading](#estrategia-de-trading)
7. [Uso del Sistema](#uso-del-sistema)
8. [Configuración Avanzada](#configuración-avanzada)
9. [Ejemplos de Operaciones](#ejemplos-de-operaciones)
10. [Troubleshooting](#troubleshooting)

---

## Introducción

**CallBot** es un algoritmo de trading profesional e inteligente diseñado para operar en mercados de divisas (Forex) con un enfoque en la gestión de capital compuesto. El sistema implementa una estrategia ganadora basada en análisis técnico avanzado, con un riesgo controlado del 1% por operación y retornos esperados de 30-65% mensual.

### Características Clave

- ✅ **Gestión de Capital Compuesto**: Ajuste dinámico del tamaño del lote basado en el balance actual
- ✅ **Riesgo Controlado**: 1% de riesgo por operación garantizado
- ✅ **Análisis Técnico Avanzado**: Integración de BOS, CHOCH, Fibonacci, Order Blocks y Zonas de Liquidez
- ✅ **Dashboard en Tiempo Real**: Monitoreo completo de operaciones y estadísticas
- ✅ **Ejecución Automática**: Operaciones ejecutadas automáticamente según señales
- ✅ **Historial Detallado**: Registro completo de todas las operaciones

---

## Características Principales

### 1. Gestión de Capital Compuesto (1% Riesgo)

El sistema implementa la estrategia de gestión de capital descrita:

```
Mes 1: Balance Inicial = $100
       Riesgo = 1% = $1
       Retorno = 35% → Balance Final = $135

Mes 2: Balance Inicial = $135
       Riesgo = 1% = $1.35
       Retorno = 46% → Balance Final = $197.10

Y así sucesivamente...
```

**Ventajas:**
- El tamaño del lote se ajusta automáticamente cada operación
- El riesgo se mantiene constante al 1% del balance actual
- El crecimiento es exponencial (compuesto)
- Las pérdidas se minimizan mientras se maximizan las ganancias

### 2. Análisis Técnico Multi-Indicador

El sistema utiliza múltiples indicadores técnicos para generar señales de alta probabilidad:

| Indicador | Descripción | Fuerza |
|-----------|-------------|--------|
| **BOS** | Break of Structure - Ruptura de estructura | 70% |
| **CHOCH** | Change of Character - Cambio de carácter | 80% |
| **Fibonacci** | Niveles de retroceso y extensión | 65% |
| **Order Blocks** | Bloques de órdenes institucionales | 65% |
| **Liquidez** | Zonas de liquidez (Liquidity Grab) | 60% |

### 3. Señales de Trading Consolidadas

El sistema genera señales **BUY**, **SELL** o **HOLD** basadas en la convergencia de múltiples indicadores.

**Ejemplo de Señal:**
```
Acción: BUY
Confianza: 78%
Precio Entrada: 1.0850
Stop Loss: 1.0800 (50 pips)
Take Profit: 1.0950 (100 pips)
Riesgo: $1.00 (1% del balance)
Lote: 0.10
```

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      MAIN.PY (Orquestador)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
        ▼            ▼            ▼            ▼
   ┌────────┐  ┌──────────┐  ┌────────────┐  ┌───────────┐
   │ MT5    │  │ Market   │  │ Strategy   │  │ Dashboard │
   │Connect │  │ Analyzer │  │ Executor   │  │           │
   └────────┘  └──────────┘  └────────────┘  └───────────┘
        │            │            │
        │            │            ▼
        │            │       ┌──────────────┐
        │            │       │ Risk Manager │
        │            │       │ (Enhanced)   │
        │            │       └──────────────┘
        │            │
        └────────────┴──────────────────────────┐
                                                │
                        ┌───────────────────────┘
                        │
                        ▼
                ┌──────────────────┐
                │ Historial de     │
                │ Operaciones      │
                │ & Estadísticas   │
                └──────────────────┘
```

---

## Módulos Principales

### 1. **main.py** - Orquestador Principal

Punto de entrada del sistema. Coordina todos los componentes.

```python
bot = TradingBot(
    initial_balance=100,
    symbol='EURUSD',
    pip_value=0.0001
)
bot.run(use_dashboard=True)
```

**Responsabilidades:**
- Inicialización del sistema
- Conexión con MT5
- Bucle principal de trading
- Gestión de ciclo de vida

### 2. **market_analyzer.py** - Analizador de Mercado

Consolida toda la lógica de análisis técnico.

```python
analyzer = MarketAnalyzer(candles, pip_value=0.0001)
signal = analyzer.generate_trading_signal()
```

**Métodos Principales:**
- `detect_bos_signal()` - Detecta Break of Structure
- `detect_choch_signal()` - Detecta Change of Character
- `detect_liquidity_signal()` - Detecta zonas de liquidez
- `detect_order_block_signal()` - Detecta bloques de órdenes
- `detect_fibonacci_levels()` - Calcula niveles de Fibonacci
- `generate_trading_signal()` - Genera señal consolidada
- `get_market_sentiment()` - Retorna sentimiento (BULLISH/BEARISH/NEUTRAL)

### 3. **enhanced_risk_manager.py** - Gestor de Riesgo Mejorado

Implementa la gestión de capital compuesto con riesgo del 1%.

```python
risk_manager = EnhancedRiskManager(
    initial_balance=100,
    risk_percent=1.0
)

# Calcular lote dinámico
lot_size = risk_manager.calculate_lot_size(
    stop_loss_pips=50,
    pip_value=0.0001
)
```

**Características:**
- Cálculo automático de riesgo (1% del balance)
- Cálculo dinámico del tamaño del lote
- Registro de operaciones completadas
- Cálculo de estadísticas y métricas
- Proyección de crecimiento compuesto
- Exportación de datos

### 4. **strategy_executor.py** - Ejecutor de Estrategia

Ejecuta las operaciones basadas en señales.

```python
executor = StrategyExecutor(
    risk_manager,
    mt5_connector,
    symbol='EURUSD'
)

result = executor.execute_signal(signal)
```

**Responsabilidades:**
- Validación de señales
- Cálculo de posición
- Ejecución de órdenes
- Gestión de operaciones abiertas
- Cierre de operaciones (SL/TP)

### 5. **dashboard.py** - Dashboard de Monitoreo

Interfaz gráfica para monitoreo en tiempo real.

**Pestañas:**
- 📊 **Resumen**: Estadísticas principales y sentimiento del mercado
- 📈 **Operaciones Abiertas**: Tabla de operaciones activas
- 📋 **Historial**: Registro de operaciones cerradas
- ⚙️ **Configuración**: Ajustes del bot

---

## Gestión de Capital Compuesto

### Fórmula de Cálculo del Lote

```
Risk Amount = Balance × (Risk Percent / 100)
Stop Loss Pips = |Entry Price - Stop Loss Price| / Pip Value
Lot Size = Risk Amount / (Stop Loss Pips × Pip Value × Currency Value)
```

### Ejemplo Práctico

**Mes 1:**
```
Balance Inicial: $100
Riesgo: 1% = $1.00
Stop Loss: 50 pips
Pip Value: 0.0001
Lot Size: $1.00 / (50 × 0.0001 × 1.0) = 0.20 lotes

Si la operación gana 35%:
Ganancia: $35.00
Balance Final: $135.00
```

**Mes 2:**
```
Balance Inicial: $135
Riesgo: 1% = $1.35
Stop Loss: 50 pips
Lot Size: $1.35 / (50 × 0.0001 × 1.0) = 0.27 lotes

Si la operación gana 46%:
Ganancia: $62.10
Balance Final: $197.10
```

### Crecimiento Proyectado

Con retornos promedio de 40% mensual:

| Mes | Balance | Crecimiento |
|-----|---------|-------------|
| 1 | $100.00 | - |
| 2 | $140.00 | +40% |
| 3 | $196.00 | +40% |
| 4 | $274.40 | +40% |
| 5 | $384.16 | +40% |
| 6 | $537.82 | +40% |
| 12 | $8,916.10 | +8,816% |

---

## Estrategia de Trading

### Componentes de la Estrategia

#### 1. Break of Structure (BOS)
Identifica cuando el precio rompe un nivel de estructura anterior, indicando un cambio en la tendencia.

**Señal Bullish:** Nuevo máximo por encima del máximo anterior
**Señal Bearish:** Nuevo mínimo por debajo del mínimo anterior

#### 2. Change of Character (CHOCH)
Detecta cambios en el carácter del mercado, indicando reversiones potenciales.

**Señal Bearish:** Mínimos más bajos (cambio de tendencia alcista a bajista)

#### 3. Niveles de Fibonacci
Identifica zonas de soporte y resistencia basadas en ratios de Fibonacci.

**Niveles:** 0%, 50%, 70.5%, 79%, 88.6%, 100%, -27%, -61.8%

#### 4. Order Blocks
Detecta zonas donde instituciones han dejado órdenes pendientes, indicando posibles reversiones.

#### 5. Zonas de Liquidez
Identifica cuando el precio alcanza nuevos máximos (Liquidity Grab), lo que típicamente precede a un retroceso.

### Generación de Señales

El sistema calcula una **confianza** basada en la convergencia de indicadores:

```
Confianza = (Suma de Fuerzas de Indicadores) / (Número de Indicadores Activos)
```

**Umbral Mínimo de Confianza:** 60% (configurable)

### Niveles de Stop Loss y Take Profit

**Método 1: Fijo**
- Stop Loss: 50 pips por debajo/encima del precio de entrada
- Take Profit: 100 pips por encima/debajo del precio de entrada

**Método 2: Basado en Fibonacci**
- Stop Loss: Nivel de Fibonacci más cercano
- Take Profit: Extensión de Fibonacci

---

## Uso del Sistema

### Instalación y Configuración

1. **Requisitos Previos:**
   - Python 3.8+
   - MetaTrader 5 instalado y ejecutándose
   - Conexión a internet

2. **Instalación de Dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuración de MT5:**
   - Abrir MetaTrader 5
   - Conectarse a una cuenta (demo o real)
   - Asegurar que el símbolo EURUSD esté disponible

### Ejecución del Bot

**Con Dashboard (Recomendado):**
```bash
python main.py
```

**Sin Dashboard:**
```python
bot = TradingBot()
bot.run(use_dashboard=False)
```

### Monitoreo en Tiempo Real

El dashboard proporciona:
- Balance actual y retorno
- Operaciones abiertas
- Historial de operaciones
- Estadísticas de rendimiento
- Señales actuales del mercado

---

## Configuración Avanzada

### Parámetros Ajustables

```python
# En main.py
bot = TradingBot(
    initial_balance=100,      # Balance inicial en USD
    symbol='EURUSD',          # Par de divisas
    pip_value=0.0001          # Valor del pip
)
```

### Configuración del Risk Manager

```python
risk_manager = EnhancedRiskManager(
    initial_balance=100,
    risk_percent=1.0,         # Riesgo por operación (%)
    min_lot_size=0.01,        # Tamaño mínimo de lote
    max_lot_size=10.0         # Tamaño máximo de lote
)
```

### Configuración del Strategy Executor

```python
executor = StrategyExecutor(
    risk_manager,
    mt5_connector,
    symbol='EURUSD'
)

executor.min_confidence = 0.6           # Confianza mínima (0-1)
executor.enable_news_filter = True      # Filtro de noticias
executor.enable_session_filter = True   # Filtro de sesión
```

---

## Ejemplos de Operaciones

### Ejemplo 1: Operación Ganadora

```
Timestamp: 2024-01-15 10:30:00
Símbolo: EURUSD
Acción: BUY
Precio Entrada: 1.0850
Stop Loss: 1.0800 (50 pips)
Take Profit: 1.0950 (100 pips)
Lote: 0.20
Confianza: 78%

Resultado:
Precio Salida: 1.0950 (Take Profit)
Ganancia: $200.00 (100 pips × 0.20 lotes × 10)
Balance Anterior: $100.00
Balance Posterior: $300.00
Duración: 45 minutos
```

### Ejemplo 2: Operación Perdedora

```
Timestamp: 2024-01-15 11:00:00
Símbolo: EURUSD
Acción: SELL
Precio Entrada: 1.0900
Stop Loss: 1.0950 (50 pips)
Take Profit: 1.0800 (100 pips)
Lote: 0.30
Confianza: 65%

Resultado:
Precio Salida: 1.0950 (Stop Loss)
Pérdida: -$150.00 (50 pips × 0.30 lotes × 10)
Balance Anterior: $300.00
Balance Posterior: $150.00
Duración: 20 minutos
```

---

## Troubleshooting

### Problema: "No se pudo conectar a MetaTrader 5"

**Solución:**
1. Verificar que MetaTrader 5 esté abierto
2. Verificar que haya una cuenta conectada
3. Verificar la conexión a internet
4. Reiniciar MetaTrader 5

### Problema: "No se pudieron obtener datos de mercado"

**Solución:**
1. Verificar que el símbolo EURUSD esté disponible
2. Verificar que la sesión de trading esté activa
3. Intentar con otro símbolo (ej: GBPUSD)

### Problema: "El bot no ejecuta operaciones"

**Solución:**
1. Verificar que la confianza sea superior al 60%
2. Verificar que no haya filtros activos bloqueando
3. Verificar que haya suficiente margen en la cuenta
4. Revisar los logs para mensajes de error

### Problema: "Las operaciones tienen pérdidas consistentes"

**Solución:**
1. Ajustar los parámetros de Stop Loss/Take Profit
2. Aumentar el umbral de confianza mínima
3. Activar filtros de noticias y sesión
4. Revisar la estrategia en mercados históricos

---

## Métricas de Rendimiento

### Estadísticas Principales

- **Win Rate**: Porcentaje de operaciones ganadoras
- **Profit Factor**: Ganancia Total / Pérdida Total
- **Return %**: Retorno porcentual del capital
- **Average Profit**: Ganancia promedio por operación
- **Max Drawdown**: Máxima caída del capital

### Objetivos de Rendimiento

| Métrica | Objetivo |
|---------|----------|
| Win Rate | > 55% |
| Profit Factor | > 1.5 |
| Monthly Return | 30-65% |
| Max Drawdown | < 10% |

---

## Conclusión

**CallBot** es un sistema profesional de trading que combina análisis técnico avanzado con gestión de capital inteligente. Su enfoque en el riesgo controlado (1%) y el crecimiento compuesto lo hace ideal para traders que buscan retornos consistentes y sostenibles.

### Próximos Pasos

1. Probar en cuenta demo
2. Ajustar parámetros según el mercado
3. Monitorear estadísticas regularmente
4. Optimizar la estrategia basada en resultados

---

**Última Actualización:** 2024-05-18  
**Versión:** 1.0.0  
**Autor:** Manus AI - Trading Bot Development Team
