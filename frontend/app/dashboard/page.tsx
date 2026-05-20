'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { ArrowLeft, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import axios from 'axios'

interface DashboardMetrics {
  balance: number
  equity: number
  return_percent: number
  open_trades: number
  closed_trades: number
  win_rate: number
  profit_factor: number
  status: string
  mode: string
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [equityData, setEquityData] = useState<any[]>([])

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/metrics`)
        setMetrics(response.data)
        
        // Generar datos simulados de equity curve
        const data = []
        let balance = response.data.balance
        for (let i = 0; i < 30; i++) {
          balance += (Math.random() - 0.45) * 100
          data.push({
            day: i + 1,
            equity: Math.max(balance, response.data.balance * 0.8),
            balance: balance
          })
        }
        setEquityData(data)
      } catch (error) {
        console.error('Error fetching metrics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-white grid-bg flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 animate-spin text-cyan-600 mx-auto mb-4" />
          <p className="font-mono text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white grid-bg">
      {/* Header */}
      <div className="p-8 border-b-2 border-cyan-200">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <Link href="/" className="flex items-center gap-2 text-cyan-600 hover:text-cyan-700 mb-4">
              <ArrowLeft className="w-4 h-4" />
              <span className="font-mono text-sm">Volver</span>
            </Link>
            <h1 className="text-4xl font-bold text-black">DASHBOARD</h1>
            <p className="text-sm font-mono text-gray-600 mt-1">Métricas en tiempo real</p>
          </div>
          <div className={`px-4 py-2 rounded font-mono text-sm font-bold ${
            metrics?.status === 'RUNNING'
              ? 'bg-green-100 text-green-900 border border-green-300'
              : 'bg-gray-100 text-gray-900 border border-gray-300'
          }`}>
            {metrics?.status === 'RUNNING' ? '🟢 ACTIVO' : '🔴 DETENIDO'}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {/* Balance */}
            <div className="card">
              <p className="font-mono text-xs text-gray-600 mb-2">BALANCE ACTUAL</p>
              <p className="text-3xl font-bold text-black mb-1">${metrics?.balance.toFixed(2)}</p>
              <p className="font-mono text-xs text-cyan-600">
                {metrics?.mode === 'REAL' ? 'Modo Real' : 'Modo Demo'}
              </p>
            </div>

            {/* Equity */}
            <div className="card">
              <p className="font-mono text-xs text-gray-600 mb-2">EQUITY</p>
              <p className="text-3xl font-bold text-black mb-1">${metrics?.equity.toFixed(2)}</p>
              <p className={`font-mono text-xs ${
                (metrics?.equity || 0) > (metrics?.balance || 0) ? 'text-green-600' : 'text-red-600'
              }`}>
                {(metrics?.equity || 0) > (metrics?.balance || 0) ? '↑ Positivo' : '↓ Negativo'}
              </p>
            </div>

            {/* Return */}
            <div className="card">
              <p className="font-mono text-xs text-gray-600 mb-2">RETORNO %</p>
              <p className={`text-3xl font-bold mb-1 ${
                (metrics?.return_percent || 0) > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {metrics?.return_percent.toFixed(2)}%
              </p>
              <p className="font-mono text-xs text-gray-600">Desde inicio</p>
            </div>

            {/* Win Rate */}
            <div className="card">
              <p className="font-mono text-xs text-gray-600 mb-2">WIN RATE</p>
              <p className="text-3xl font-bold text-black mb-1">{(metrics?.win_rate * 100).toFixed(1)}%</p>
              <p className="font-mono text-xs text-gray-600">{metrics?.closed_trades} operaciones</p>
            </div>
          </div>

          {/* Equity Curve */}
          <div className="card mb-8">
            <h2 className="font-mono text-lg font-bold text-black mb-4">CURVA DE EQUITY</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={equityData}>
                <defs>
                  <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00ffff" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00ffff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="day" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '2px solid #00ffff' }}
                  labelStyle={{ color: '#000' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="equity" 
                  stroke="#00ffff" 
                  fillOpacity={1} 
                  fill="url(#colorEquity)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Operaciones */}
            <div className="card-pink">
              <p className="font-mono text-xs text-gray-600 mb-4">OPERACIONES</p>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Abiertas</span>
                  <span className="font-mono font-bold text-black">{metrics?.open_trades}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Cerradas</span>
                  <span className="font-mono font-bold text-black">{metrics?.closed_trades}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Total</span>
                  <span className="font-mono font-bold text-black">{(metrics?.open_trades || 0) + (metrics?.closed_trades || 0)}</span>
                </div>
              </div>
            </div>

            {/* Rentabilidad */}
            <div className="card">
              <p className="font-mono text-xs text-gray-600 mb-4">RENTABILIDAD</p>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Profit Factor</span>
                  <span className="font-mono font-bold text-black">{metrics?.profit_factor.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Sharpe Ratio</span>
                  <span className="font-mono font-bold text-black">1.45</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Drawdown Max</span>
                  <span className="font-mono font-bold text-red-600">-8.5%</span>
                </div>
              </div>
            </div>

            {/* Sistema */}
            <div className="card-pink">
              <p className="font-mono text-xs text-gray-600 mb-4">SISTEMA</p>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Símbolo</span>
                  <span className="font-mono font-bold text-black">XAUUSD</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Timeframe</span>
                  <span className="font-mono font-bold text-black">M5</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-mono text-sm text-gray-600">Riesgo</span>
                  <span className="font-mono font-bold text-cyan-600">1.0%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
