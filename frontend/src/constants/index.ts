/**
 * 共享常量与业务映射
 */

export const CASE_TYPES = [
  {
    key: 'wage_arrears',
    name: '劳动报酬纠纷',
    desc: '工资被拖欠、加班费、离职补偿',
    icon: '💰',
  },
  {
    key: 'labor_contract',
    name: '劳动合同争议',
    desc: '无故辞退、合同解除、竞业限制',
    icon: '📄',
  },
  {
    key: 'work_injury',
    name: '工伤赔偿',
    desc: '工伤认定、伤残赔偿、医疗费',
    icon: '🏥',
  },
  {
    key: 'other',
    name: '其他法律咨询',
    desc: '社保、劳动监察等综合咨询',
    icon: '⚖️',
  },
] as const

export const CASE_TYPE_MAP: Record<string, { name: string; icon: string }> = Object.fromEntries(
  CASE_TYPES.map((item) => [item.key, { name: item.name, icon: item.icon }]),
)

export const REGION_MAP: Record<string, string> = {
  beijing: '北京',
  shanghai: '上海',
  guangdong: '广东',
}

/** 地区 key → 汉字，未知值原样返回 */
export function formatRegion(region?: string | null): string {
  if (!region) return '-'
  return REGION_MAP[region] || region
}

/** 案件类型 key → 汉字，未知值原样返回 */
export function formatCaseType(caseType?: string | null): string {
  if (!caseType) return '其他'
  return CASE_TYPE_MAP[caseType]?.name || caseType
}

export const DEFAULT_REGION = 'beijing'

export const TOOL_HINTS: Record<string, string> = {
  search_public_laws_tool: '正在检索法律条文…',
  search_public_cases_tool: '正在检索相似判例…',
  search_private_knowledge_tool: '正在检索私域知识库…',
  generate_legal_doc_tool: '正在生成法律文书…',
}

export const COMPLEXITY_MAP: Record<string, { label: string; color: string }> = {
  high: { label: '高复杂度', color: 'error' },
  medium: { label: '中等复杂度', color: 'warning' },
  low: { label: '低复杂度', color: 'success' },
}

export const LEAD_STATUS_MAP: Record<string, { label: string; type: 'info' | 'success' | 'warning' | 'default' }> = {
  open: { label: '待接单', type: 'warning' },
  claimed: { label: '已接单', type: 'success' },
  completed: { label: '已完成', type: 'default' },
}
