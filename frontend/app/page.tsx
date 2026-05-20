'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { BarChart3, TrendingUp, Shield, History, Activity, Settings, Zap } from 'lucide-react'

export default function Home() {
  const [botStatus, setBotStatus] = useState('STOPPED')

  useEffect(() => {
    // Conectar a WebSocket para estado del bot
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL + '/ws/trading')
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'state_update') {
        setBotStatus(data.data.status)
      }
    }

    return () => ws.close()
  }, [])

  const sections = [
    {
      title: 'Dashboard',
      description: 'Métricas principales y estado de la cuenta',
      icon: BarChart3,
      href: '/dashboard',
      color: 'cyan',
    },
    {
      title: 'Señales',
      description: 'Análisis SMC: BOS, CHOCH, Order Blocks, FVG',
      href: '/signals',
      color: 'pink',
    },
    {
      title: 'Gestión de Riesgo',
      description: 'Sistema cuantitativo: 1% dinámico, VaR, CVaR',
      href: '/risk',
      color: 'cyan',
    },
    {
      title: 'Historial',
      description: 'Registro detallado de todas las operaciones',
      href: '/history',
      color: 'pink',
    },
    {
      title: 'Backtesting',
      description: 'Análisis histórico con métricas profesionales',
      href: '/backtest',
      color: 'cyan',
    },
    {
      title: 'Configuración',
      description: 'Parámetros del bot y conexión MT5',
      href: '/config',
      color: 'pink',
    },
  ]

  return (
    <div className="min-h-screen bg-white" style={{
      backgroundImage: `
        linear-gradient(0deg, transparent 24%, rgba(0, 255, 255, 0.05) 25%, rgba(0, 255, 255, 0.05) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, 0.05) 75%, rgba(0, 255, 255, 0.05) 76%, transparent 77%, transparent),
        linear-gradient(90deg, transparent 24%, rgba(0, 255, 255, 0.05) 25%, rgba(0, 255, 255, 0.05) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, 0.05) 75%, rgba(0, 255, 255, 0.05) 76%, transparent 77%, transparent)
      `,
      backgroundSize: '50px 50px',
    }}>
      {/* Header */}
      <div className="p-8 border-b-2 border-cyan-200">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-5xl font-bold text-black mb-2">XAUUSD Quant Bot</h1>
          <p className="text-lg font-mono text-gray-600">Sistema Algorítmico de Trading Profesional con IA</p>
          <div className="flex items-center gap-4 mt-4">
            <div className={`px-4 py-2 rounded font-mono text-sm ${
              botStatus === 'RUNNING' 
                ? 'bg-green-100 text-green-900 border border-green-300' 
                : 'bg-gray-100 text-gray-900 border border-gray-300'
            }`}>
              {botStatus === 'RUNNING' ? '🟢 BOT ACTIVO' : '🔴 BOT DETENIDO'}
            </div>
          </div>
          <div className="h-1 bg-gradient-to-r from-cyan-300 via-pink-300 to-transparent rounded-full opacity-50 mt-6"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {sections.map((section) => {
              const Icon = section.icon
              const isCyan = section.color === 'cyan'
              return (
                <Link key={section.href} href={section.href}>
                  <div className={`p-6 rounded-lg border-2 cursor-pointer transition-all hover:shadow-lg ${
                    isCyan 
                      ? 'border-cyan-200 hover:border-cyan-400 bg-white' 
                      : 'border-pink-200 hover:border-pink-400 bg-white'
                  }`}>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="font-mono text-lg font-bold text-black">{section.title}</h3>
                        <p className="font-mono text-xs text-gray-600 mt-1">{section.description}</p>
                      </div>
                      <Icon className={`w-8 h-8 ${
                        isCyan ? 'text-cyan-600' : 'text-pink-600'
                      }`} />
                    </div>
                    <button className={`w-full py-2 rounded font-mono text-xs font-bold text-white transition-all ${
                      isCyan
                        ? 'bg-cyan-600 hover:bg-cyan-700'
                        : 'bg-pink-600 hover:bg-pink-700'
                    }`}>
                      Acceder →
                    </button>
                  </div>
                </Link>
              )
            })}
          </div>

          {/* Features Highlight */}
          <div className="border-2 border-cyan-200 bg-gradient-to-r from-cyan-50 to-pink-50 rounded-lg p-8">
            <h2 className="font-mono text-2xl font-bold text-black mb-6">Características Principales</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-cyan-600 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-mono font-bold text-black">Análisis SMC Avanzado</p>
                    <p className="font-mono text-xs text-gray-600">BOS, CHOCH, Order Blocks, FVG, Liquidez, Fibonacci</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-pink-600 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-mono font-bold text-black">Gestión de Riesgo Cuantitativa</p>
                    <p className="font-mono text-xs text-gray-600">1% dinámico, VaR, CVaR, Circuit Breaker, Kelly Fraccional</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-cyan-600 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-mono font-bold text-black">Modelos de IA Integrados</p>
                    <p className="font-mono text-xs text-gray-600">XGBoost, LSTM, Meta-modelo con explicaciones LLM</p>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-pink-600 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-mono font-bold text-black">Backtesting Profesional</p>
                    <p className="font-mono text-xs text-gray-600">Sharpe, Sortino, Calmar, Recovery Factor, Drawdown</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-cyan-600 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-mono font-bold text-black">Integración MT5 Real</p>
                    <p className="font-mono text-xs text-gray-600">Conexión en vivo con reconexión automática</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-pink-600 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="font-mono font-bold text-black">Notificaciones Inteligentes</p>
                    <p className="font-mono text-xs text-gray-600">Alertas automáticas con explicaciones en lenguaje natural</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
