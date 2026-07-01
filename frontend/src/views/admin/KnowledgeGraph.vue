<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识图谱可视化</span>
          <div class="header-actions">
            <el-button size="small" :loading="loading" @click="fetchData">刷新数据</el-button>
            <el-tag v-if="!loading" type="success">{{ nodes.length }} 节点 · {{ links.length }} 关系</el-tag>
          </div>
        </div>
      </template>

      <div ref="chartRef" style="width:100%;height:550px;"></div>

      <el-alert
        title="知识图谱基于知识库文件和故障案例自动构建。拖拽节点可查看关系，滚轮缩放。"
        type="info"
        :closable="false"
        show-icon
        style="margin-top:16px;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const chartRef = ref(null)
const loading = ref(false)
const nodes = ref([])
const links = ref([])
let chart = null

// 类别定义
const categories = [
  { name: '设备', itemStyle: { color: '#409eff' } },
  { name: '知识文件', itemStyle: { color: '#67c23a' } },
  { name: '故障类型', itemStyle: { color: '#e6a23c' } },
  { name: '部件', itemStyle: { color: '#f56c6c' } },
  { name: '标准规范', itemStyle: { color: '#909399' } }
]

// 设备关键词映射
const DEVICE_KEYWORDS = ['电梯', '扶梯', '自动扶梯', '曳引机', '门系统', '控制系统', '安全回路']
const COMPONENT_KEYWORDS = ['光幕', '门机', '导靴', '钢丝绳', '制动器', '变频器', '限速器', '缓冲器', '编码器', '传感器']
const STANDARD_KEYWORDS = ['GB', 'TSG', 'EN', 'ISO']

function detectCategory(name) {
  for (const kw of STANDARD_KEYWORDS) if (name.includes(kw)) return 4
  for (const kw of COMPONENT_KEYWORDS) if (name.includes(kw)) return 3
  for (const kw of DEVICE_KEYWORDS) if (name.includes(kw)) return 0
  return 1 // 默认知识文件
}

async function fetchData() {
  loading.value = true
  try {
    // 并行获取知识文件列表 + 故障案例列表
    const [filesRes, faultsRes] = await Promise.all([
      request.get('/api/knowledge/files'),
      request.get('/api/faults')
    ])

    const files = (filesRes?.items || filesRes || [])
    const faults = (faultsRes?.items || faultsRes || [])

    const nodeMap = new Map()
    const edgeSet = new Set()
    const graphNodes = []
    const graphLinks = []

    function addNode(id, name, category, size) {
      if (!nodeMap.has(id)) {
        nodeMap.set(id, true)
        graphNodes.push({ id, name, symbolSize: size || 30, category })
      }
    }

    function addLink(source, target) {
      const key = [source, target].sort().join('::')
      if (!edgeSet.has(key)) {
        edgeSet.add(key)
        graphLinks.push({ source, target })
      }
    }

    // 核心节点：电梯
    addNode('elevator_root', '智能电梯系统', 0, 55)
    addNode('escalator_root', '自动扶梯系统', 0, 50)

    // 从知识文件构建节点
    for (const f of files) {
      const fname = f.original_filename || f.filename || '未知文件'
      const cat = detectCategory(fname)
      addNode('file_' + f.id, fname, cat, cat === 0 ? 40 : 28)
      addLink('elevator_root', 'file_' + f.id)
    }

    // 从故障报告构建节点和关系
    for (const fault of faults) {
      const fname = fault.device_name || fault.title || '未知故障'
      addNode('fault_' + fault.id, fname, 2, 28)
      addLink('elevator_root', 'fault_' + fault.id)

      if (fault.device_name) {
        const devNodeId = 'dev_' + fault.device_name
        addNode(devNodeId, fault.device_name, 0, 35)
        addLink('fault_' + fault.id, devNodeId)
      }

      if (fault.description) {
        for (const kw of COMPONENT_KEYWORDS) {
          if (fault.description.includes(kw)) {
            const compId = 'comp_' + kw
            addNode(compId, kw, 3, 24)
            addLink('fault_' + fault.id, compId)
          }
        }
      }
    }

    // 添加电梯子系统
    const subsystems = ['门系统', '曳引机', '控制系统', '安全回路', '轿厢', '导轨系统']
    for (const sub of subsystems) {
      addNode('sub_' + sub, sub, 1, 35)
      addLink('elevator_root', 'sub_' + sub)
    }

    nodes.value = graphNodes
    links.value = graphLinks

    renderChart()
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chart) return
  chart.setOption({
    title: { text: '电梯维保知识图谱', left: 'center', top: 8, textStyle: { fontSize: 16 } },
    tooltip: {
      formatter: (params) => {
        if (params.dataType === 'node') return params.name
        return `${params.data.source} → ${params.data.target}`
      }
    },
    legend: { data: categories.map(c => c.name), bottom: 10 },
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      categories,
      nodes: nodes.value,
      links: links.value,
      force: { repulsion: 350, edgeLength: [80, 200], gravity: 0.08 },
      label: { show: true, fontSize: 11, color: '#303133' },
      lineStyle: { color: '#c0c4cc', curveness: 0.25, width: 1 },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 2.5 }
      }
    }]
  })
}

onMounted(async () => {
  const echarts = (await import('echarts')).default || (await import('echarts'))
  chart = echarts.init(chartRef.value)
  window.addEventListener('resize', () => chart?.resize())
  await fetchData()
})

onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; align-items: center; gap: 12px; }
</style>
