<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>工单消息提醒</span>
          <el-button type="primary" size="small" @click="fetchMessages" :loading="loading">刷新消息</el-button>
        </div>
      </template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="新工单" name="new_order" />
        <el-tab-pane label="审核结果" name="audit" />
      </el-tabs>
      <el-empty v-if="!filteredMessages.length" description="暂无消息" :image-size="100" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="msg in filteredMessages"
          :key="msg.id"
          :timestamp="msg.time"
          :type="msg.type"
          placement="top"
        >
          <el-card shadow="hover" class="msg-card">
            <div class="msg-header">
              <el-tag size="small" :type="msg.tagType">{{ msg.tag }}</el-tag>
              <span class="msg-title">{{ msg.title }}</span>
            </div>
            <p class="msg-body">{{ msg.content }}</p>
            <div class="msg-footer" v-if="msg.action">
              <el-button size="small" type="primary" text @click="goAction(msg)">{{ msg.action }}</el-button>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/api/request'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('all')
const messages = ref([])

const filteredMessages = computed(() => {
  if (activeTab.value === 'all') return messages.value
  return messages.value.filter(m => m.category === activeTab.value)
})

function buildMessages(orders, cases) {
  const msgs = []
  const now = new Date().toISOString().slice(0, 10)

  // 待处理工单
  ;(orders || []).filter(o => o.status === 'pending' || o.status === 'assigned').slice(0, 10).forEach(o => {
    msgs.push({
      id: `order_${o.id}`,
      title: `新工单: ${o.title || o.template_name || `#${o.id}`}`,
      content: `设备: ${o.device_name || '-'}，请及时处理`,
      time: o.created_at ? o.created_at.slice(0, 10) : now,
      type: 'warning',
      tag: '新工单',
      tagType: 'warning',
      category: 'new_order',
      action: '查看工单',
      path: '/worker/inspections'
    })
  })

  // 审核结果
  ;(cases || []).filter(c => c.status === 'approved' || c.status === 'rejected').slice(0, 10).forEach(c => {
    const isApproved = c.status === 'approved'
    msgs.push({
      id: `case_${c.id}`,
      title: `案例审核${isApproved ? '通过' : '驳回'}: ${c.title || `#${c.id}`}`,
      content: c.audit_comment || (isApproved ? '您的案例已通过审核' : '您的案例被驳回，请修改后重新提交'),
      time: c.updated_at ? c.updated_at.slice(0, 10) : now,
      type: isApproved ? 'success' : 'danger',
      tag: '审核结果',
      tagType: isApproved ? 'success' : 'danger',
      category: 'audit',
      action: '查看详情',
      path: '/worker/case-report'
    })
  })

  msgs.sort((a, b) => b.time.localeCompare(a.time))
  return msgs
}

async function fetchMessages() {
  loading.value = true
  try {
    const [ordersRes, casesRes] = await Promise.all([
      request.get('/api/inspections/orders?limit=100'),
      request.get('/api/cases?limit=100')
    ])
    const orders = ordersRes?.items || ordersRes || []
    const cases = casesRes?.items || casesRes || []
    messages.value = buildMessages(orders, cases)
  } catch {} finally { loading.value = false }
}

function goAction(msg) {
  if (msg.path) router.push(msg.path)
}

onMounted(fetchMessages)
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.msg-card { cursor: pointer; }
.msg-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.msg-title { font-weight: 600; }
.msg-body { color: #606266; font-size: 14px; line-height: 1.6; }
.msg-footer { margin-top: 8px; }
</style>
