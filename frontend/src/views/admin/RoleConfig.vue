<template>
  <div class="role-config-page">
    <div class="page-header">
      <h2>角色与权限配置</h2>
      <el-button type="primary" @click="openCreate">新增角色</el-button>
    </div>

    <el-table :data="roles" v-loading="loading" stripe border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="角色名称" min-width="140">
        <template #default="{ row }">
          <el-tag :type="row.name === 'admin' ? 'danger' : row.name === 'worker' ? 'warning' : 'info'" effect="dark">
            {{ row.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="180">
        <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" :disabled="row.name === 'admin'" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑 Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑角色' : '新增角色'"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="角色名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入角色名称（英文）"
            :disabled="isEdit"
            maxlength="32"
          />
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
            maxlength="100"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoles, createRole, updateRole, deleteRole } from '@/api/users'

const roles = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref(null)
const editingId = ref(null)

const form = reactive({
  name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

function formatTime(str) {
  if (!str) return '-'
  return new Date(str).toLocaleString('zh-CN')
}

async function fetchRoles() {
  loading.value = true
  try {
    const res = await getRoles()
    roles.value = res || []
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '获取角色列表失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  form.name = ''
  form.description = ''
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editingId.value = row.id
  form.name = row.name
  form.description = row.description || ''
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value) {
      await updateRole(editingId.value, {
        name: form.name,
        description: form.description
      })
      ElMessage.success('角色更新成功')
    } else {
      await createRole({
        name: form.name,
        description: form.description
      })
      ElMessage.success('角色创建成功')
    }
    dialogVisible.value = false
    await fetchRoles()
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || err?.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  if (row.name === 'admin') return
  try {
    await ElMessageBox.confirm(`确定删除角色「${row.name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await deleteRole(row.id)
    ElMessage.success('角色删除成功')
    await fetchRoles()
  } catch (err) {
    if (err !== 'cancel' && err?.response) {
      ElMessage.error(err?.response?.data?.message || err?.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(fetchRoles)
</script>

<style scoped>
.role-config-page {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #303133;
}
</style>
