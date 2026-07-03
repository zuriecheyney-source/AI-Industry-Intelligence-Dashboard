import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI行业情报系统',
  description: '自动化采集和推送行业情报的智能系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}