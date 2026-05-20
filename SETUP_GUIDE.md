# 🚀 XAUUSD Quant Bot - Guía de Instalación y Uso

## 📋 Requisitos Previos

- **Python 3.8+** instalado
- **Node.js 18+** instalado (para frontend)
- **MetaTrader 5** instalado y ejecutándose
- **Cuenta de trading** (demo o real)
- **Git** (opcional)

---

## 🔧 Instalación

### 1. Clonar o descargar el repositorio

```bash
cd CallBot
```

### 2. Configurar Backend Python

#### 2.1 Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 2.3 Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales MT5
# MT5_LOGIN=tu_numero_cuenta
# MT5_PASSWORD=tu_contraseña
# MT5_SERVER=Exness-MT5
```

#### 2.4 Iniciar servidor FastAPI

```bash
python -m uvicorn api.fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

El servidor estará disponible en: `http://localhost:8000`

### 3. Configurar Frontend React/Next.js

#### 3.1 Instalar dependencias

```bash
cd frontend
npm install
```

#### 3.2 Crear archivo .env.local

```bash
# En la carpeta frontend/
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local
```

#### 3.3 Iniciar servidor de desarrollo

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:3000`

---

## 🎮 Uso del Sistema

### Acceder al Dashboard

1. Abrir navegador: `http://localhost:3000`
2. Verás la página de inicio con acceso a todas las secciones

### Secciones Principales

#### 📊 Dashboard (`/dashboard`)
- Métricas en tiempo real: balance, equity, retorno %
- Estadísticas: win rate, profit factor, Sharpe ratio
- Curva de equity histórica
- Estado del bot (activo/detenido)

#### 📈 Señales (`/signals`)
- Análisis SMC en tiempo real
- BOS (Break of Structure)
- CHOCH (Change of Character)
- Order Blocks
- Fair Value Gaps (FVG)
- Zonas de Liquidez
- Niveles de Fibonacci
- Confianza de cada señal

#### 🛡️ Gestión de Riesgo (`/risk`)
- Cálculo del 1% dinámico
- Calculadora de lotaje
- Value at Risk (VaR)
- Conditional VaR (CVaR)
- Curva de capital compuesto
- Circuit breaker

#### 📋 Historial (`/history`)
- Tabla de todas las operaciones cerradas
- Filtros por dirección (BUY/SELL)
- Búsqueda por ID/fecha
- Estadísticas consolidadas

#### 📊 Backtesting (`/backtest`)
- Ejecutar backtests históricos
- Seleccionar rango de fechas
- Visualizar equity curve
- Métricas profesionales (Sharpe, Sortino, Calmar)
- Exportar reportes

#### ⚙️ Configuración (`/config`)
- Parámetros de estrategia
- Modo simulación vs. real
- Filtros de sesión (Londres, NY, Tokio)
- Credenciales MT5
- Parámetros SMC

---

## 🔌 Integración MT5

### Conexión Automática

El bot se conectará automáticamente a MT5 con las credenciales en `.env`:

```
MT5_LOGIN=tu_numero_cuenta
MT5_PASSWORD=tu_contraseña
MT5_SERVER=Exness-MT5
```

### Reconexión Automática

Si la conexión se pierde, el bot intentará reconectarse automáticamente hasta 5 veces.

### Modo Demo vs. Real

- **Demo**: Usa datos sintéticos realistas (sin conexión MT5)
- **Real**: Conecta en vivo a MetaTrader 5 (requiere credenciales válidas)

Cambiar en `/config` → General → Modo de Operación

---

## 📊 Análisis SMC (Smart Money Concepts)

### Break of Structure (BOS)
- Ruptura de máximo/mínimo anterior
- Confianza: 70-95%
- Señal de cambio de tendencia

### Change of Character (CHOCH)
- Cambio en patrón de velas
- Confianza: 60-85%
- Debilitamiento de tendencia

### Order Blocks (OB)
- Velas impulsivas grandes
- Confianza: 75-90%
- Precios tienden a volver

### Fair Value Gaps (FVG)
- Espacios entre velas
- Confianza: 65-80%
- Mercado tiende a llenarlos

### Zonas de Liquidez
- Acumulación de máximos/mínimos
- Confianza: 70-85%
- Instituciones buscan liquidez

### Fibonacci
- Retrocesos: 23.6%, 38.2%, 50%, 61.8%, 78.6%
- Extensiones: 127.2%, 161.8%, 200%, 261.8%
- Confianza: 60-75%

---

## 💰 Gestión de Riesgo

### Sistema del 1% Dinámico

```
Riesgo por Op. = Balance × 1% = $100 (si balance = $10,000)
Lotaje = Riesgo / (Distancia SL en pips × Pip Value)
```

### Ejemplo

```
Balance:        $10,000
Riesgo:         1% = $100
Entrada:        2045.50
Stop Loss:      2040.00
Distancia:      5.50 pips
Lotaje:         0.1 lotes (aproximado)
```

### Circuit Breaker

- **Pérdida Diaria Máxima**: 5% del balance
- **Drawdown Máximo**: 20% del peak balance
- Si se activa: Bot se detiene automáticamente

---

## 🤖 Modelos de IA (Próximamente)

- **XGBoost**: Predicción de dirección
- **LSTM**: Series temporales
- **Meta-modelo**: Ensemble de predicciones
- **Explicaciones LLM**: Por qué cada señal

---

## 📈 Métricas Profesionales

### Rendimiento
- Retorno Total y %
- Win Rate
- Profit Factor

### Riesgo
- **Sharpe Ratio**: >1.0 es bueno
- **Sortino Ratio**: Penaliza solo downside
- **Calmar Ratio**: Retorno / Drawdown máximo
- **Recovery Factor**: Ganancia / Drawdown máximo
- **VaR 95%**: Pérdida máxima esperada
- **CVaR 95%**: Promedio de pérdidas en tail risk

---

## 🐛 Troubleshooting

### Error: "No se pudo conectar a MetaTrader 5"

**Soluciones:**
1. Verificar que MetaTrader 5 esté abierto
2. Verificar que haya una cuenta conectada
3. Revisar credenciales en `.env`
4. Reiniciar MetaTrader 5

### Error: "API no responde"

**Soluciones:**
1. Verificar que el servidor FastAPI esté corriendo: `http://localhost:8000/health`
2. Revisar logs en terminal
3. Reiniciar servidor: `Ctrl+C` y ejecutar de nuevo

### Error: "Frontend no carga"

**Soluciones:**
1. Verificar que el servidor Next.js esté corriendo en puerto 3000
2. Limpiar caché: `npm run build`
3. Revisar consola del navegador (F12)

---

## 📚 Documentación Adicional

- **DESIGN.md** - Arquitectura del sistema
- **TRADING_SYSTEM_DOCUMENTATION.md** - Documentación completa
- **PROYECTO_README.md** - Guía del usuario

---

## 🚀 Próximos Pasos

1. ✅ Configurar MT5 con credenciales reales
2. ✅ Ejecutar backtesting en modo demo
3. ✅ Validar señales en modo simulación
4. ✅ Comenzar con capital pequeño en modo real
5. ✅ Monitorear regularmente

---

## ⚠️ Disclaimer

**AVISO IMPORTANTE:**

Este software se proporciona "tal cual" sin garantías. El trading implica riesgo significativo de pérdida. Aunque ha sido diseñado profesionalmente, no hay garantía de rentabilidad.

**Recomendaciones:**
- Probar primero en cuenta demo
- Comenzar con capital pequeño
- Monitorear regularmente
- No invertir dinero que no puedas perder

---

## 📞 Soporte

Para preguntas o reportar issues:
1. Revisar logs en `.manus-logs/`
2. Verificar configuración en `/config`
3. Ejecutar backtest para validar estrategia
4. Contactar al propietario del bot

---

**¡Bienvenido a XAUUSD Quant Bot! Que tus operaciones sean rentables.** 🚀📈
