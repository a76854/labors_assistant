<script setup lang="ts">
import { computed } from 'vue'
import {
  AttachOutline,
  BookmarksOutline,
  BulbOutline,
  BusinessOutline,
  CashOutline,
  ChatbubblesOutline,
  CheckmarkCircle,
  CheckmarkOutline,
  ChevronBack,
  ChevronDown,
  ChevronForward,
  CloudUploadOutline,
  CodeSlashOutline,
  DocumentTextOutline,
  DownloadOutline,
  EllipsisHorizontal,
  ExpandOutline,
  FileTrayFullOutline,
  FilterOutline,
  FolderOpenOutline,
  GridOutline,
  HardwareChipOutline,
  HandRightOutline,
  HelpCircleOutline,
  HomeOutline,
  ListOutline,
  LocateOutline,
  LogOutOutline,
  MedkitOutline,
  MenuOutline,
  MoonOutline,
  PaperPlaneOutline,
  PersonCircleOutline,
  PersonOutline,
  PieChartOutline,
  PulseOutline,
  RocketOutline,
  ScaleOutline,
  SearchOutline,
  SettingsOutline,
  ShieldCheckmarkOutline,
  SparklesOutline,
  SquareOutline,
  StarOutline,
  StatsChartOutline,
  StopCircleOutline,
  SunnyOutline,
  SyncOutline,
  TextOutline,
  TrashOutline,
  WarningOutline,
  LockClosedOutline,
  MailOutline,
  PhonePortraitOutline,
} from '@vicons/ionicons5'

const props = withDefaults(
  defineProps<{
    name: string
    size?: number | string
    color?: string
  }>(),
  {
    size: 16,
    color: 'currentColor',
  },
)

const ICON_MAP: Record<string, unknown> = {
  attach: AttachOutline,
  bookmark: BookmarksOutline,
  bulb: BulbOutline,
  briefcase: BusinessOutline,
  cash: CashOutline,
  chat: ChatbubblesOutline,
  check: CheckmarkOutline,
  'check-circle': CheckmarkCircle,
  'chevron-left': ChevronBack,
  'chevron-right': ChevronForward,
  'chevron-down': ChevronDown,
  cloud: CloudUploadOutline,
  code: CodeSlashOutline,
  document: DocumentTextOutline,
  download: DownloadOutline,
  ellipsis: EllipsisHorizontal,
  expand: ExpandOutline,
  file: FileTrayFullOutline,
  filter: FilterOutline,
  folder: FolderOpenOutline,
  grid: GridOutline,
  hardware: HardwareChipOutline,
  'hand-right': HandRightOutline,
  help: HelpCircleOutline,
  home: HomeOutline,
  list: ListOutline,
  locate: LocateOutline,
  logout: LogOutOutline,
  medkit: MedkitOutline,
  menu: MenuOutline,
  moon: MoonOutline,
  'paper-plane': PaperPlaneOutline,
  person: PersonOutline,
  'person-circle': PersonCircleOutline,
  'pie-chart': PieChartOutline,
  pulse: PulseOutline,
  rocket: RocketOutline,
  scale: ScaleOutline,
  search: SearchOutline,
  settings: SettingsOutline,
  shield: ShieldCheckmarkOutline,
  sparkles: SparklesOutline,
  square: SquareOutline,
  star: StarOutline,
  stats: StatsChartOutline,
  stop: StopCircleOutline,
  sun: SunnyOutline,
  sync: SyncOutline,
  text: TextOutline,
  trash: TrashOutline,
  warning: WarningOutline,
  lock: LockClosedOutline,
  mail: MailOutline,
  phone: PhonePortraitOutline,
}

const iconComponent = computed(() => ICON_MAP[props.name])
const sizePx = computed(() => {
  const v = props.size
  return typeof v === 'number' ? `${v}px` : v
})
</script>

<template>
  <span
    v-if="iconComponent"
    class="app-icon-box"
    :style="{ width: sizePx, height: sizePx }"
    aria-hidden="true"
  >
    <component :is="iconComponent" :size="String(size)" :style="{ color }" />
  </span>
  <span v-else class="app-icon-box app-icon-fallback" :style="{ width: sizePx, height: sizePx }">?</span>
</template>

<style scoped>
.app-icon-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  line-height: 0;
}
.app-icon-box :deep(svg) {
  width: 100% !important;
  height: 100% !important;
}
.app-icon-box :deep(.ionicon) {
  width: 100% !important;
  height: 100% !important;
}
.app-icon-fallback {
  color: var(--text-tertiary);
}
</style>
