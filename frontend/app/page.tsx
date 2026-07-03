'use client'

import { useEffect, useState } from 'react'
import { apiClient, Intelligence } from '@/lib/api-client'
import IntelligenceCard from '@/components/IntelligenceCard'
import FilterPanel from '@/components/FilterPanel'
import TrendChart from '@/components/TrendChart'

export default function Home() {
  const [intelligence, setIntelligence] = useState<Intelligence[]>([])
  const [loading, setLoading] = useState(true)
  const [showStats, setShowStats] = useState(false)
  const [filters, setFilters] = useState({
    industry: '',
    keyword: '',
    page: 1,
    dateMode: 'today' as 'today' | 'history',
  })
  const [total, setTotal] = useState(0)

  useEffect(() => {
    loadIntelligence()
  }, [filters])

  const loadIntelligence = async () => {
    setLoading(true)
    try {
      const todayStr = new Date().toISOString().split('T')[0]
      const response = await apiClient.getIntelligence({
        industry: filters.industry || undefined,
        keyword: filters.keyword || undefined,
        start_date: filters.dateMode === 'today' ? todayStr : '2020-01-01',
        end_date: filters.dateMode === 'today' ? todayStr : todayStr,
        page: filters.page,
        page_size: 20,
      })
      setIntelligence(response.items)
      setTotal(response.total)
    } catch (error) {
      console.error('加载情报失败:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-200">
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>
      
      <header className="sticky top-0 z-50 bg-white/70 backdrop-blur-md border-b border-slate-200/50 shadow-sm transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 tracking-tight">
                AI Industry Intelligence
              </h1>
            </div>
            <nav className="flex items-center space-x-6">
              <a href="/" className="text-sm font-semibold text-indigo-600 relative after:absolute after:-bottom-5 after:left-0 after:right-0 after:h-0.5 after:bg-indigo-600">
                看板
              </a>
              <a href="/config" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">
                配置
              </a>
              <button
                onClick={() => setShowStats(!showStats)}
                className="text-sm font-medium px-4 py-2 rounded-full bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
              >
                {showStats ? '隐藏统计' : '查看统计'}
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        {showStats && (
          <div className="mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
            <TrendChart />
          </div>
        )}

        <div className="mb-8 relative z-10">
          <FilterPanel
            filters={filters}
            onFilterChange={setFilters}
            onRefresh={loadIntelligence}
          />
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="relative w-16 h-16">
              <div className="absolute inset-0 rounded-full border-t-2 border-indigo-500 animate-spin"></div>
              <div className="absolute inset-2 rounded-full border-t-2 border-violet-400 animate-spin-reverse"></div>
            </div>
          </div>
        ) : intelligence.length === 0 ? (
          <div className="text-center py-24 bg-white/50 backdrop-blur-sm rounded-2xl border border-slate-200 border-dashed">
            <div className="w-16 h-16 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-slate-900">暂无情报数据</h3>
            <p className="mt-1 text-slate-500">调整筛选条件或等待系统收集新的数据</p>
          </div>
        ) : (
          <div className="animate-in fade-in duration-500">
            <div className="mb-6 flex justify-between items-center text-sm text-slate-500 font-medium">
              <span>发现 {total} 条高价值情报</span>
              <span>第 {filters.page} 页</span>
            </div>
            
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {intelligence.map((item, index) => (
                <div key={index} className="animate-in slide-in-from-bottom-4 duration-500 fill-mode-both" style={{ animationDelay: `${index * 50}ms` }}>
                  <IntelligenceCard intelligence={item} />
                </div>
              ))}
            </div>

            {/* 分页 */}
            {total > 20 && (
              <div className="mt-12 flex justify-center items-center space-x-3">
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                  disabled={filters.page === 1}
                  className="px-5 py-2.5 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-xl disabled:opacity-50 hover:bg-slate-50 hover:border-slate-300 transition-all font-medium text-slate-700 shadow-sm disabled:hover:bg-white"
                >
                  上一页
                </button>
                <div className="px-5 py-2.5 rounded-xl bg-slate-100 font-medium text-slate-600 border border-transparent">
                  <span className="text-slate-900">{filters.page}</span> / {Math.ceil(total / 20)}
                </div>
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                  disabled={filters.page >= Math.ceil(total / 20)}
                  className="px-5 py-2.5 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-xl disabled:opacity-50 hover:bg-slate-50 hover:border-slate-300 transition-all font-medium text-slate-700 shadow-sm disabled:hover:bg-white"
                >
                  下一页
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}