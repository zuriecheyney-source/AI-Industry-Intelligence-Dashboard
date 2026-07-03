'use client'

import { useState, useEffect } from 'react'
import { apiClient, IndustryConfig } from '@/lib/api-client'

interface Props {
  filters: {
    industry: string
    keyword: string
    page: number
    dateMode: 'today' | 'history'
  }
  onFilterChange: (filters: any) => void
  onRefresh: () => void
}

export default function FilterPanel({ filters, onFilterChange, onRefresh }: Props) {
  const [industries, setIndustries] = useState<IndustryConfig[]>([])
  const [localKeyword, setLocalKeyword] = useState(filters.keyword)

  useEffect(() => {
    loadIndustries()
  }, [])

  const loadIndustries = async () => {
    try {
      const data = await apiClient.getIndustries()
      setIndustries(data.filter(i => i.enabled))
    } catch (error) {
      console.error('加载行业配置失败:', error)
    }
  }

  const handleSearch = () => {
    onFilterChange({ ...filters, keyword: localKeyword, page: 1 })
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="bg-white/70 backdrop-blur-md rounded-2xl border border-slate-200/60 p-6 shadow-sm">
      <div className="flex flex-col md:flex-row gap-5 mb-5 items-start md:items-center justify-between border-b border-slate-100 pb-5">
        <div className="flex items-center space-x-2 bg-slate-100/80 p-1 rounded-xl">
          <button
            onClick={() => onFilterChange({ ...filters, dateMode: 'today', page: 1 })}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filters.dateMode === 'today'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
            }`}
          >
            今日情报
          </button>
          <button
            onClick={() => onFilterChange({ ...filters, dateMode: 'history', page: 1 })}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filters.dateMode === 'history'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
            }`}
          >
            历史所有
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div>
          <label className="block text-xs font-semibold tracking-wider text-slate-500 uppercase mb-2">
            行业筛选
          </label>
          <div className="relative">
            <select
              value={filters.industry}
              onChange={(e) =>
                onFilterChange({ ...filters, industry: e.target.value, page: 1 })
              }
              className="w-full appearance-none pl-4 pr-10 py-2.5 bg-white border border-slate-200 rounded-xl text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-sm"
            >
              <option value="">全部行业</option>
              {industries.map((ind) => (
                <option key={ind.name} value={ind.name}>
                  {ind.name}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        <div className="md:col-span-2">
          <label className="block text-xs font-semibold tracking-wider text-slate-500 uppercase mb-2">
            关键词搜索
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              value={localKeyword}
              onChange={(e) => setLocalKeyword(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="搜索标题或摘要..."
              className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-sm placeholder:text-slate-400"
            />
          </div>
        </div>

        <div className="flex items-end gap-3">
          <button
            onClick={handleSearch}
            className="flex-1 px-4 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500/20 transition-all shadow-md shadow-indigo-500/20"
          >
            搜索
          </button>
          <button
            onClick={onRefresh}
            className="px-4 py-2.5 bg-white text-slate-700 text-sm font-medium rounded-xl border border-slate-200 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm flex items-center justify-center group"
            title="刷新数据"
          >
            <svg className="w-4 h-4 text-slate-500 group-hover:text-slate-700 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}