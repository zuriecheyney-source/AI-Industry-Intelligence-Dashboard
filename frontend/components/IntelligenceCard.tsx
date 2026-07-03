import { Intelligence } from '@/lib/api-client'

interface Props {
  intelligence: Intelligence
}

export default function IntelligenceCard({ intelligence }: Props) {
  const importanceColors = {
    '高': 'bg-rose-500/10 text-rose-600 border-rose-500/20',
    '中': 'bg-amber-500/10 text-amber-600 border-amber-500/20',
    '低': 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20',
  }

  const categoryColors = {
    '政策': 'bg-blue-500/10 text-blue-600',
    '竞品': 'bg-fuchsia-500/10 text-fuchsia-600',
    '研报': 'bg-indigo-500/10 text-indigo-600',
    '动态': 'bg-slate-500/10 text-slate-600',
  }

  return (
    <div className="group relative bg-white/70 backdrop-blur-md rounded-2xl border border-slate-200/60 p-6 shadow-sm hover:shadow-xl hover:shadow-indigo-500/10 hover:border-indigo-200/60 transition-all duration-300 flex flex-col h-full overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-white/40 to-white/0 pointer-events-none rounded-2xl"></div>
      
      <div className="relative z-10 flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">{intelligence.date}</span>
        </div>
        <span
          className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${
            importanceColors[intelligence.importance as keyof typeof importanceColors] || 'bg-slate-100 text-slate-600 border-slate-200'
          }`}
        >
          {intelligence.importance}重要
        </span>
      </div>

      <h3 className="relative z-10 text-lg font-bold text-slate-800 mb-3 line-clamp-2 leading-snug group-hover:text-indigo-600 transition-colors duration-200">
        {intelligence.title}
      </h3>

      <p className="relative z-10 text-sm text-slate-500 mb-5 line-clamp-3 flex-grow leading-relaxed">
        {intelligence.summary}
      </p>

      <div className="relative z-10 mt-auto">
        <div className="flex flex-wrap gap-2 mb-4">
          <span
            className={`text-xs font-medium px-2.5 py-1 rounded-md ${
              categoryColors[intelligence.category as keyof typeof categoryColors] || 'bg-slate-100 text-slate-600'
            }`}
          >
            {intelligence.category}
          </span>
          <span className="text-xs font-medium px-2.5 py-1 rounded-md bg-slate-100 text-slate-600">
            {intelligence.industry}
          </span>
        </div>

        {intelligence.keywords && intelligence.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-5">
            {intelligence.keywords.map((keyword, index) => (
              <span
                key={index}
                className="text-[11px] px-2 py-0.5 bg-slate-50 border border-slate-100 text-slate-500 rounded-full hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
              >
                #{keyword}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center">
              <svg className="w-3 h-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <span className="text-xs font-medium text-slate-500 truncate max-w-[120px]">
              {intelligence.source_name || '未知来源'}
            </span>
          </div>
          <a
            href={intelligence.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="group/link flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
          >
            阅读原文
            <svg className="w-3 h-3 transform group-hover/link:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  )
}