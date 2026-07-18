<template>
  <div class="worker-home">
    <section class="hero-panel">
      <div class="hero-copy">
        <span class="eyebrow">FIELD WORKFLOW</span>
        <h1>{{ greeting }}，{{ userName }}</h1>
        <p>按现场作业顺序完成今天的维保任务：接单、点检、检索、记录，每一步都有知识库和智能建议辅助。</p>
      </div>
      <div class="hero-status">
        <div class="status-orbit">
          <span class="orbit-core">{{ pendingOrders }}</span>
        </div>
        <div>
          <strong>待处理工单</strong>
          <small>优先完成已分配和进行中的任务</small>
        </div>
      </div>
    </section>

    <section class="flow-panel">
      <div class="section-heading">
        <div>
          <span class="eyebrow">TODAY</span>
          <h2>今日维保流程</h2>
        </div>
        <el-button type="primary" plain @click="$router.push('/worker/inspections')">查看全部工单</el-button>
      </div>

      <div class="workflow-steps">
        <button
          v-for="(step, index) in workflow"
          :key="step.title"
          class="workflow-card"
          :class="{ active: index === activeStepIndex }"
          @click="$router.push(step.path)"
        >
          <span class="step-index">0{{ index + 1 }}</span>
          <span class="step-icon">
            <el-icon><component :is="step.icon" /></el-icon>
          </span>
          <strong>{{ step.title }}</strong>
          <small>{{ step.desc }}</small>
          <em>{{ step.meta }}</em>
        </button>
      </div>
    </section>

    <section class="content-grid">
      <div class="glass-panel task-panel">
        <div class="panel-title">
          <div>
            <span class="eyebrow">NEXT</span>
            <h3>下一项任务</h3>
          </div>
          <el-tag :type="nextTask ? statusType(nextTask.status) : 'info'" effect="light">
            {{ nextTask ? statusLabel(nextTask.status) : '暂无任务' }}
          </el-tag>
        </div>

        <div v-if="nextTask" class="next-task">
          <div class="task-device">
            <span class="device-dot"></span>
            <div>
              <strong>{{ nextTask.order_name || nextTask.title || `工单 #${nextTask.id}` }}</strong>
              <small>{{ nextTask.device_name || `设备 ID：${nextTask.device_id || '-'}` }}</small>
            </div>
          </div>
          <p>{{ nextTask.remark || '请按点检标准逐项确认设备状态，异常项及时备注并上传现场照片。' }}</p>
          <div class="task-actions">
            <el-button type="primary" @click="$router.push('/worker/inspections')">
              {{ nextTask.status === 'in_progress' ? '继续执行' : '开始处理' }}
            </el-button>
            <el-button plain @click="$router.push('/worker/knowledge')">查知识库</el-button>
          </div>
        </div>
        <el-empty v-else description="当前没有待处理工单" :image-size="90" />
      </div>

      <div class="glass-panel assist-panel">
        <div class="panel-title">
          <div>
            <span class="eyebrow">ASSIST</span>
            <h3>现场辅助</h3>
          </div>
        </div>
        <div class="assist-list">
          <button v-for="item in assistActions" :key="item.title" @click="$router.push(item.path)">
            <span :class="['assist-icon', item.tone]">
              <el-icon><component :is="item.icon" /></el-icon>
            </span>
            <span>
              <strong>{{ item.title }}</strong>
              <small>{{ item.desc }}</small>
            </span>
          </button>
        </div>
      </div>
    </section>

    <section class="mini-stats">
      <div v-for="stat in stats" :key="stat.label" class="mini-stat">
        <span>{{ stat.label }}</span>
        <strong>{{ stat.value }}</strong>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import request from '@/api/request'
import { Checked, ChatLineRound, Collection, DocumentChecked, Search, Warning } from '@element-plus/icons-vue'

const userStore = useUserStore()
const loading = ref(false)
const orders = ref([])
const recentRecords = ref([])
const caseCount = ref(0)
const summary = ref({})

function cleanDisplayName(value) {
  if (!value || /^[?\s]+$/.test(value)) return ''
  return value
}

const userName = computed(() => cleanDisplayName(userStore.userInfo?.real_name) || userStore.userInfo?.username || '维保师傅')
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 11) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const pendingOrders = computed(() => orders.value.filter((o) => !['completed', 'cancelled'].includes(o.status)).length)
const nextTask = computed(() => {
  const priority = { in_progress: 0, pending: 1, assigned: 2 }
  return [...orders.value]
    .filter((o) => !['completed', 'cancelled'].includes(o.status))
    .sort((a, b) => (priority[a.status] ?? 9) - (priority[b.status] ?? 9))[0]
})
const activeStepIndex = computed(() => {
  if (pendingOrders.value > 0) return 0
  if ((summary.value.fault_report_count || 0) > 0) return 2
  return 3
})

const workflow = computed(() => [
  { title: '接收任务', desc: '查看分配工单和设备位置', meta: `${pendingOrders.value} 项待处理`, icon: Checked, path: '/worker/inspections' },
  { title: '现场点检', desc: '逐项填写结果、备注和照片', meta: '标准化执行', icon: DocumentChecked, path: '/worker/inspections' },
  { title: '故障研判', desc: '检索知识库并生成检修建议', meta: '知识辅助', icon: Search, path: '/worker/faults' },
  { title: '沉淀记录', desc: '生成维保记录并上报案例', meta: `${recentRecords.value.length} 条近期记录`, icon: Warning, path: '/worker/maintenance' }
])

const assistActions = [
  { title: '知识库查询', desc: '快速查规程、手册和案例', icon: Collection, tone: 'blue', path: '/worker/knowledge' },
  { title: '智能检修建议', desc: '结合故障描述生成步骤建议', icon: ChatLineRound, tone: 'green', path: '/worker/repair-advice' },
  { title: '故障案例上报', desc: '把现场经验沉淀为知识', icon: Warning, tone: 'amber', path: '/worker/case-report' }
]

const stats = computed(() => [
  { label: '待处理', value: pendingOrders.value },
  { label: '本月完成', value: summary.value.inspection_order_count || 0 },
  { label: '维保记录', value: recentRecords.value.length },
  { label: '上报案例', value: caseCount.value }
])

function statusLabel(status) {
  const map = { pending: '待开始', assigned: '已分配', in_progress: '进行中', completed: '已完成', overdue: '已逾期' }
  return map[status] || status || '待处理'
}

function statusType(status) {
  const map = { pending: 'warning', assigned: 'warning', in_progress: 'primary', completed: 'success', overdue: 'danger' }
  return map[status] || 'info'
}

onMounted(async () => {
  loading.value = true
  try {
    const [summaryRes, ordersRes, recordsRes, casesRes] = await Promise.all([
      request.get('/api/dashboard/summary'),
      request.get('/api/inspections/orders?limit=8'),
      request.get('/api/dashboard/recent-maintenance-records'),
      request.get('/api/cases?limit=100')
    ])
    summary.value = summaryRes || {}
    orders.value = ordersRes?.items || ordersRes || []
    recentRecords.value = Array.isArray(recordsRes) ? recordsRes.slice(0, 6) : []
    const cases = casesRes?.items || casesRes || []
    caseCount.value = Array.isArray(cases) ? cases.length : 0
  } catch {
    orders.value = []
    recentRecords.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.worker-home {
  display: flex;
  flex-direction: column;
  gap: 22px;
  max-width: 100%;
  overflow: hidden;
  max-width: 1520px;
  margin: 0 auto;
}

.hero-panel,
.flow-panel,
.glass-panel,
.mini-stat {
  border: 1px solid rgba(255, 255, 255, 0.66);
  background: rgba(255, 255, 255, 0.66);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 24px 70px -28px rgba(15, 40, 80, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.82);
}

.hero-panel {
  min-height: 188px;
  border-radius: 22px;
  padding: 30px 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}

.hero-panel::after {
  content: '';
  position: absolute;
  width: 420px;
  height: 420px;
  right: -130px;
  top: -160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.14), rgba(16, 185, 129, 0.06) 48%, transparent 70%);
  filter: blur(6px);
}

.hero-copy,
.hero-status {
  position: relative;
  z-index: 1;
}

.eyebrow {
  display: inline-flex;
  color: #2563EB;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  margin-bottom: 8px;
}

.hero-copy h1,
.section-heading h2,
.panel-title h3 {
  margin: 0;
  color: #0F172A;
}

.hero-copy h1 {
  font-size: clamp(1.8rem, 3vw, 2.35rem);
  line-height: 1.08;
  letter-spacing: -0.03em;
}

.hero-copy p {
  max-width: 620px;
  margin: 12px 0 0;
  color: #64748B;
  line-height: 1.8;
}

.hero-status {
  display: flex;
  align-items: center;
  gap: 18px;
  min-width: 250px;
  justify-content: flex-end;
}

.status-orbit {
  width: 86px;
  height: 86px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: conic-gradient(from 90deg, #2563EB, #10B981, #A78BFA, #2563EB);
  box-shadow: 0 16px 34px rgba(37, 99, 235, 0.22);
}

.orbit-core {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  display: grid;
  place-items: center;
  color: #0F172A;
  font-size: 1.75rem;
  font-weight: 800;
}

.hero-status strong,
.hero-status small,
.workflow-card strong,
.workflow-card small,
.workflow-card em,
.task-device strong,
.task-device small,
.assist-list strong,
.assist-list small,
.mini-stat span,
.mini-stat strong {
  display: block;
}

.hero-status small {
  margin-top: 6px;
  color: #64748B;
}

.flow-panel,
.glass-panel {
  border-radius: 22px;
  padding: 24px;
  box-sizing: border-box;
}

.section-heading,
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.workflow-card {
  min-width: 0;
  min-height: 170px;
  border: 1px solid #E2E8F0;
  border-radius: 18px;
  background: #FFFFFF;
  padding: 18px;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  color: #1E293B;
  position: relative;
  overflow: hidden;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.workflow-card::after {
  content: '';
  position: absolute;
  right: -40px;
  bottom: -70px;
  width: 130px;
  height: 130px;
  border-radius: 50%;
  background: rgba(37, 99, 235, 0.06);
}

.workflow-card:hover,
.workflow-card.active {
  transform: translateY(-4px);
  border-color: rgba(37, 99, 235, 0.32);
  box-shadow: 0 18px 40px -24px rgba(37, 99, 235, 0.42);
}

.workflow-card:focus-visible,
.assist-list button:focus-visible {
  outline: 3px solid rgba(36, 168, 107, 0.22);
  outline-offset: 2px;
}

.workflow-card:active,
.assist-list button:active {
  transform: scale(0.98);
}

.step-index {
  color: #CBD5E1;
  font-weight: 800;
  font-size: 0.78rem;
}

.step-icon {
  width: 42px;
  height: 42px;
  margin: 16px 0 14px;
  border-radius: 13px;
  display: grid;
  place-items: center;
  color: #2563EB;
  background: #EFF6FF;
}

.workflow-card.active .step-icon {
  color: #FFFFFF;
  background: linear-gradient(135deg, #2563EB, #10B981);
}

.workflow-card strong,
.workflow-card small,
.workflow-card em {
  position: relative;
  z-index: 1;
}

.workflow-card small {
  margin-top: 7px;
  color: #64748B;
  line-height: 1.5;
}

.workflow-card em {
  margin-top: 14px;
  color: #10B981;
  font-style: normal;
  font-size: 0.8rem;
  font-weight: 700;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr);
  gap: 22px;
  min-width: 0;
}

.next-task {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.task-device {
  display: flex;
  align-items: center;
  gap: 14px;
}

.device-dot {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, #2563EB, #38BDF8);
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.2);
}

.task-device small,
.next-task p {
  color: #64748B;
}

.next-task p {
  margin: 0;
  line-height: 1.8;
}

.task-actions {
  display: flex;
  gap: 12px;
}

.assist-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assist-list button {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #E2E8F0;
  background: #FFFFFF;
  border-radius: 15px;
  padding: 14px;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.assist-list button:hover {
  transform: translateX(3px);
  border-color: #BFDBFE;
}

.assist-icon {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
}

.assist-icon.blue { color: #2563EB; background: #EFF6FF; }
.assist-icon.green { color: #16A34A; background: #F0FDF4; }
.assist-icon.amber { color: #D97706; background: #FFFBEB; }

.assist-list small {
  margin-top: 4px;
  color: #64748B;
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.mini-stat {
  border-radius: 18px;
  padding: 18px 20px;
}

.mini-stat span {
  color: #64748B;
}

.mini-stat strong {
  margin-top: 8px;
  font-size: 1.7rem;
  color: #0F172A;
}

@media (max-width: 1100px) {
  .workflow-steps,
  .mini-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .hero-panel,
  .hero-status,
  .section-heading,
  .panel-title {
    align-items: flex-start;
  }

  .hero-panel,
  .section-heading,
  .panel-title {
    flex-direction: column;
  }

  .workflow-steps,
  .mini-stats {
    grid-template-columns: 1fr;
  }
}
</style>
