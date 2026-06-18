<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button text @click="$router.push('/admin/inspection-templates')">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
          <span>{{ isEdit ? '编辑点检模板' : '创建点检模板' }}</span>
        </div>
      </template>

      <el-form :model="form" label-width="100px" style="max-width: 800px; margin: 0 auto;" size="large">
        <el-form-item label="模板名称" required>
          <el-input v-model="form.template_name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="设备类型" required>
          <el-select v-model="form.device_type" placeholder="请选择设备类型" style="width:100%">
            <el-option label="曳引电梯" value="traction_elevator" />
            <el-option label="液压电梯" value="hydraulic_elevator" />
            <el-option label="自动扶梯" value="escalator" />
            <el-option label="自动人行道" value="moving_walkway" />
          </el-select>
        </el-form-item>
        <el-form-item label="点检类型" required>
          <el-select v-model="form.inspection_type" placeholder="请选择点检类型" style="width:100%">
            <el-option label="日常点检" value="daily" />
            <el-option label="月度点检" value="monthly" />
            <el-option label="季度点检" value="quarterly" />
            <el-option label="年度点检" value="annual" />
            <el-option label="故障点检" value="fault" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="可选描述信息" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>

        <!-- 点检步骤 -->
        <el-divider content-position="left">点检步骤</el-divider>
        <div v-for="(step, idx) in form.steps" :key="idx" class="step-card">
          <div class="step-header">
            <span class="step-index">步骤 {{ idx + 1 }}</span>
            <el-button type="danger" text @click="removeStep(idx)">删除此步骤</el-button>
          </div>
          <el-form-item label="检查区域" required>
            <el-input v-model="step.area" placeholder="如：机房、轿厢、井道" />
          </el-form-item>
          <el-form-item label="检查项目" required>
            <el-input v-model="step.item_name" placeholder="如：曳引钢丝绳磨损检查" />
          </el-form-item>
          <el-form-item label="检查内容" required>
            <el-input v-model="step.item_content" type="textarea" :rows="2" placeholder="详细描述检查内容" />
          </el-form-item>
          <el-form-item label="判断标准">
            <el-input v-model="step.standard" placeholder="如：磨损量 < 10%" />
          </el-form-item>
          <el-form-item label="选项">
            <el-checkbox v-model="step.required_photo">需拍照</el-checkbox>
            <el-checkbox v-model="step.required_remark">需备注</el-checkbox>
          </el-form-item>
        </div>

        <el-button @click="addStep" style="width:100%; border-style:dashed; margin:12px 0;">
          + 添加步骤
        </el-button>

        <el-form-item style="margin-top:24px;">
          <el-button @click="$router.push('/admin/inspection-templates')">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存模板</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)

const emptyStep = () => ({
  step_order: 1,
  area: '',
  item_name: '',
  item_content: '',
  standard: '',
  required_photo: false,
  required_remark: false
})

const form = ref({
  template_name: '',
  device_type: '',
  inspection_type: '',
  description: '',
  is_active: true,
  steps: [emptyStep()]
})

function addStep() {
  form.value.steps.push({ ...emptyStep(), step_order: form.value.steps.length + 1 })
}
function removeStep(idx) {
  form.value.steps.splice(idx, 1)
  form.value.steps.forEach((s, i) => s.step_order = i + 1)
}

async function fetchTemplate() {
  try {
    const res = await request.get(`/api/inspections/templates/${route.params.id}`)
    const d = res || {}
    form.value.template_name = d.template_name || ''
    form.value.device_type = d.device_type || ''
    form.value.inspection_type = d.inspection_type || ''
    form.value.description = d.description || ''
    form.value.is_active = d.is_active !== false
    if (d.steps?.length) {
      form.value.steps = d.steps.map((s, i) => ({
        step_order: i + 1,
        area: s.area || '',
        item_name: s.item_name || '',
        item_content: s.item_content || '',
        standard: s.standard || '',
        required_photo: !!s.required_photo,
        required_remark: !!s.required_remark
      }))
    }
  } catch {
    ElMessage.error('获取模板信息失败')
  }
}

async function handleSave() {
  if (!form.value.template_name || !form.value.device_type || !form.value.inspection_type) {
    ElMessage.warning('请填写模板名称、设备类型和点检类型')
    return
  }
  if (!form.value.steps.length) {
    ElMessage.warning('请至少添加一个点检步骤')
    return
  }
  saving.value = true
  try {
    const payload = {
      ...form.value,
      steps: form.value.steps.map((s, i) => ({ ...s, step_order: i + 1 }))
    }
    if (isEdit.value) {
      await request.put(`/api/inspections/templates/${route.params.id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/api/inspections/templates', payload)
      ElMessage.success('创建成功')
    }
    router.push('/admin/inspection-templates')
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (isEdit.value) fetchTemplate()
})
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; align-items: center; gap: 12px; }
.step-card {
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 16px 20px 4px;
  margin-bottom: 12px;
  background: #fafbfc;
}
.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.step-index {
  font-weight: 600;
  color: #409eff;
  font-size: 14px;
}
</style>
