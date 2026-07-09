export interface Intelligence {
  date: string
  industry: string
  title: string
  summary: string
  source_url: string
  source_name?: string
  category: string
  importance: string
  keywords: string[]
}

export interface IntelligenceResponse {
  total: number
  page: number
  page_size: number
  items: Intelligence[]
}

export interface IndustryConfig {
  name: string
  keywords: string[]
  enabled: boolean
}

export interface Statistics {
  total_files: number
  total_intelligence: number
  by_industry: Record<string, number>
  by_month: Record<string, number>
}

// 后端 API 地址：开发环境使用环境变量，生产环境可通过代理或环境变量配置
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}/api${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `API Error: ${response.status}`)
  }

  return response.json()
}

export const apiClient = {
  // 情报查询
  getIntelligence: (params: {
    industry?: string
    start_date?: string
    end_date?: string
    keyword?: string
    page?: number
    page_size?: number
  }): Promise<IntelligenceResponse> => {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value))
      }
    })
    return fetchAPI<IntelligenceResponse>(`/intelligence?${searchParams}`)
  },

  // 统计信息
  getStatistics: (): Promise<Statistics> => {
    return fetchAPI<Statistics>('/intelligence/statistics')
  },

  // 行业配置
  getIndustries: (): Promise<IndustryConfig[]> => {
    return fetchAPI<IndustryConfig[]>('/industries')
  },

  createIndustry: (industry: IndustryConfig): Promise<IndustryConfig> => {
    return fetchAPI<IndustryConfig>('/industries', {
      method: 'POST',
      body: JSON.stringify(industry),
    })
  },

  updateIndustry: (name: string, industry: IndustryConfig): Promise<IndustryConfig> => {
    return fetchAPI<IndustryConfig>(`/industries/${encodeURIComponent(name)}`, {
      method: 'PUT',
      body: JSON.stringify(industry),
    })
  },

  deleteIndustry: (name: string): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>(`/industries/${encodeURIComponent(name)}`, {
      method: 'DELETE',
    })
  },

  // 任务管理
  triggerTask: (): Promise<{ message: string; timestamp: string }> => {
    return fetchAPI<{ message: string; timestamp: string }>('/tasks/trigger', {
      method: 'POST',
    })
  },

  getTaskStatus: (): Promise<any> => {
    return fetchAPI<any>('/tasks/status')
  },

  // 企业微信测试
  testNotificationPush: (): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>('/notification/test', {
      method: 'POST',
    })
  },

  // 系统配置
  getAIProvider: (): Promise<{ provider: string; model: string }> => {
    return fetchAPI<{ provider: string; model: string }>('/config/ai-provider')
  },

  getScheduleConfig: (): Promise<{ times: string[]; timezone: string }> => {
    return fetchAPI<{ times: string[]; timezone: string }>('/config/schedule')
  },
}