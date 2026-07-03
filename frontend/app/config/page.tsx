'use client'

import { useEffect, useState } from 'react'
import { apiClient, IndustryConfig } from '@/lib/api-client'

export default function ConfigPage() {
  const [industries, setIndustries] = useState<IndustryConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<string | null>(null)
  const [formData, setFormData] = useState<IndustryConfig>({
    name: '',
    keywords: [],
    enabled: true,
  })
  const [keywordInput, setKeywordInput] = useState('')
  const [aiProvider, setAIProvider] = useState('')
  const [scheduleConfig, setScheduleConfig] = useState<{ times: string[]; timezone: string } | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [industriesData, providerData, scheduleData] = await Promise.all([
        apiClient.getIndustries(),
        apiClient.getAIProvider(),
        apiClient.getScheduleConfig(),
      ])
      setIndustries(industriesData)
      setAIProvider(providerData.provider)
      setScheduleConfig(scheduleData)
    } catch (error) {
      console.error('加载配置失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      if (editing) {
        await apiClient.updateIndustry(editing, formData)
      } else {
        await apiClient.createIndustry(formData)
      }
      setEditing(null)
      setFormData({ name: '', keywords: [], enabled: true })
      setKeywordInput('')
      loadData()
    } catch (error) {
      alert('保存失败: ' + (error as Error).message)
    }
  }

  const handleDelete = async (name: string) => {
    if (!confirm(`确定要删除行业"${name}"吗？`)) return
    try {
      await apiClient.deleteIndustry(name)
      loadData()
    } catch (error) {
      alert('删除失败: ' + (error as Error).message)
    }
  }

  const handleEdit = (industry: IndustryConfig) => {
    setEditing(industry.name)
    setFormData(industry)
    setKeywordInput(industry.keywords.join(', '))
  }

  const handleAddKeyword = () => {
    if (!keywordInput.trim()) return
    const newKeywords = keywordInput.split(/[,，]/).map(k => k.trim()).filter(k => k)
    setFormData({ ...formData, keywords: [...new Set([...formData.keywords, ...newKeywords])] })
    setKeywordInput('')
  }

  const handleRemoveKeyword = (keyword: string) => {
    setFormData({
      ...formData,
      keywords: formData.keywords.filter(k => k !== keyword),
    })
  }

  const handleTriggerTask = async () => {
    try {
      const result = await apiClient.triggerTask()
      alert(result.message)
    } catch (error) {
      alert('触发任务失败: ' + (error as Error).message)
    }
  }

  const handleTestNotification = async () => {
    try {
      const result = await apiClient.testNotificationPush()
      alert(result.message)
    } catch (error) {
      alert('测试失败: ' + (error as Error).message)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">系统配置</h1>
            <nav className="space-x-4">
              <a href="/" className="text-gray-600 hover:text-gray-900">
                看板
              </a>
              <a href="/config" className="text-blue-600 font-medium">
                配置
              </a>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* 系统信息 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">系统信息</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-500">AI提供商</div>
              <div className="text-lg font-medium text-gray-900">{aiProvider}</div>
            </div>
            {scheduleConfig && (
              <>
                <div>
                  <div className="text-sm text-gray-500">定时任务</div>
                  <div className="text-lg font-medium text-gray-900">
                    {scheduleConfig.times.join(', ')}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">时区</div>
                  <div className="text-lg font-medium text-gray-900">
                    {scheduleConfig.timezone}
                  </div>
                </div>
              </>
            )}
          </div>
          <div className="mt-4 space-x-2">
            <button
              onClick={handleTriggerTask}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              手动触发采集
            </button>
            <button
              onClick={handleTestNotification}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              测试飞书推送
            </button>
          </div>
        </div>

        {/* 行业配置 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">行业配置</h2>

          {/* 编辑表单 */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-md font-medium text-gray-900 mb-3">
              {editing ? '编辑行业' : '添加新行业'}
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  行业名称
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  disabled={!!editing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  placeholder="例如：AI板块"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  关键词（用逗号分隔）
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={keywordInput}
                    onChange={(e) => setKeywordInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="输入关键词，按回车添加"
                  />
                  <button
                    onClick={handleAddKeyword}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    添加
                  </button>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {formData.keywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {keyword}
                      <button
                        onClick={() => handleRemoveKeyword(keyword)}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enabled}
                  onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 text-sm text-gray-700">启用</label>
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={handleSave}
                  disabled={!formData.name || formData.keywords.length === 0}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {editing ? '更新' : '添加'}
                </button>
                {editing && (
                  <button
                    onClick={() => {
                      setEditing(null)
                      setFormData({ name: '', keywords: [], enabled: true })
                      setKeywordInput('')
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    取消
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* 行业列表 */}
          <div className="space-y-3">
            {industries.map((industry) => (
              <div
                key={industry.name}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h4 className="font-medium text-gray-900">{industry.name}</h4>
                    {!industry.enabled && (
                      <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                        已禁用
                      </span>
                    )}
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {industry.keywords.map((keyword) => (
                      <span
                        key={keyword}
                        className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(industry)}
                    className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    编辑
                  </button>
                  <button
                    onClick={() => handleDelete(industry.name)}
                    className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}