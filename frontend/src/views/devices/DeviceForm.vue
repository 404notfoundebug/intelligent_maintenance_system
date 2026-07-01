<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button text @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
          <span>{{ isEdit ? '编辑设备' : '新增设备' }}</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
        style="max-width: 680px; margin: 0 auto;"
        size="large"
      >
        <el-form-item label="设备名称" prop="device_name">
          <el-input v-model="form.device_name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备编号" prop="device_code">
          <el-input v-model="form.device_code" placeholder="请输入唯一设备编号" />
        </el-form-item>
        <el-form-item label="设备类型" prop="device_type">
          <el-select v-model="form.device_type" placeholder="请选择设备类型" style="width:100%">
            <el-option label="曳引电梯" value="traction_elevator" />
            <el-option label="液压电梯" value="hydraulic_elevator" />
            <el-option label="自动扶梯" value="escalator" />
            <el-option label="自动人行道" value="moving_walkway" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备型号">
          <el-input v-model="form.device_model" placeholder="请输入设备型号" />
        </el-form-item>
        <el-form-item label="生产厂家">
          <el-input v-model="form.manufacturer" placeholder="请输入生产厂家" />
        </el-form-item>
        <el-form-item label="安装地点">
          <el-input v-model="form.installation_location" placeholder="请输入安装地点" />
        </el-form-item>
        <el-form-item label="维保单位">
          <el-input v-model="form.maintenance_company" placeholder="请输入维保单位" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="form.responsible_person" placeholder="请输入负责人姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="设备状态" prop="status">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="正常" value="normal" />
            <el-option label="维保中" value="maintenance" />
            <el-option label="故障" value="fault" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="可选备注信息" />
        </el-form-item>

        <el-form-item>
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const deviceId = computed(() => route.params.id)
const saving = ref(false)
const formRef = ref(null)

const form = ref({
  device_name: '',
  device_code: '',
  device_type: '',
  device_model: '',
  manufacturer: '',
  installation_location: '',
  maintenance_company: '',
  responsible_person: '',
  contact_phone: '',
  status: 'normal',
  remark: ''
})

const rules = {
  device_name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  device_code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  device_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择设备状态', trigger: 'change' }]
}

async function fetchDevice() {
  try {
    const res = await request.get(`/api/devices/${deviceId.value}`)
    const d = res || {}
    Object.keys(form.value).forEach(k => {
      if (d[k] !== undefined) form.value[k] = d[k]
    })
  } catch {
    ElMessage.error('获取设备信息失败')
  }
}

async function handleSave() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      await request.put(`/api/devices/${deviceId.value}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await request.post('/api/devices', form.value)
      ElMessage.success('创建成功')
    }
    router.push('/admin/devices')
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (isEdit.value) fetchDevice()
})
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; align-items: center; gap: 12px; }
</style>
