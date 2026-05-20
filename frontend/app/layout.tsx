import type { Metadata } from 'next'
import { Toaster } from 'react-hot-toast'
import './globals.css'

export const metadata: Metadata = {
  title: 'XAUUSD Quant Bot - Trading Algorítmico Profesional',
  description: 'Sistema de trading algorítmico para XAUUSD con IA, gestión de riesgo y análisis SMC',
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="bg-white text-gray-900">
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  )
}
