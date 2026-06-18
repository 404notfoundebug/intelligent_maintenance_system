<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddDialog">新增用户</el-button>
        </div>
      </template>
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'primary' : 'success'">{{ row.role === 'admin' ? '管理员' : '维修工人' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="360">
          <template #default="{ row }">
            <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="showRoleDialog(row)">角色</el-button>
            <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="handleToggle(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" @click="showResetDialog(row)">重置密码</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑用户 Dialog -->
    <el-dialog v-model="formDialogVisible" :title="formMode === 'add' ? '新增用户' : '编辑用户'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="formMode === 'edit'" />
        </el-form-item>
        <el-form-item label="密码" v-if="formMode === 'add'">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="管理员" value="admin" />
            <el-option label="维修工人" value="worker" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>

    <!-- 角色变更 Dialog -->
    <el-dialog v-model="roleDialogVisible" title="变更角色" width="400px">
      <el-form label-width="80px">
        <el-form-item label="用户">
          <span>{{ currentUser?.username }}</span>
        </el-form-item>
        <el-form-item label="新角色">
          <el-select v-model="newRole">
            <el-option label="管理员" value="admin" />
            <el-option label="维修工人" value="worker" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRoleConfirm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码 Dialog -->
    <el-dialog v-model="resetDialogVisible" title="重置密码" width="400px">
      <el-form label-width="100px">
        <el-form-item label="用户">
          <span>{{ currentUser?.username }}</span>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="newPassword" type="password" show-password placeholder="留空则生成随机密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetConfirm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

const users = ref([])
const loading = ref(false)

// 表单 Dialog
const formDialogVisible = ref(false)
const formMode = ref('add') // 'add' | 'edit'
const form = ref({ username: '', password: '', role: 'worker', phone: '' })
const currentUser = ref(null)

// 角色 Dialog
const roleDialogVisible = ref(false)
const newRole = ref('worker')

// 重置密码 Dialog
const resetDialogVisible = ref(false)
const newPassword = ref('')

async function fetchUsers() {
  loading.value = true
  try {
    const res = await request.get('/api/users')
    users.value = res?.items || res || []
  } catch {
    users.value = []
  } finally {
    loading.value = false
  }
}

// 新增
function showAddDialog() {
  formMode.value = 'add'
  form.value = { username: '', password: '', role: 'worker', phone: '' }
  formDialogVisible.value = true
}

// 编辑
function showEditDialog(row) {
  formMode.value = 'edit'
  currentUser.value = row
  form.value = { username: row.username, role: row.role, phone: row.phone || '' }
  formDialogVisible.value = true
}

// 保存（新增/编辑）
async function handleSave() {
  try {
    if (formMode.value === 'add') {
      await request.post('/api/users', form.value)
      ElMessage.success('创建成功')
    } else {
      await request.put(`/api/users/${currentUser.value.id}`, form.value)
      ElMessage.success('更新成功')
    }
    formDialogVisible.value = false
    fetchUsers()
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '操作失败')
  }
}

// 角色变更
function showRoleDialog(row) {
  currentUser.value = row
  newRole.value = row.role === 'admin' ? 'worker' : 'admin'
  roleDialogVisible.value = true
}
async function handleRoleConfirm() {
  try {
    await request.put(`/api/users/${currentUser.value.id}/role`, { role: newRole.value })
    ElMessage.success('角色变更成功')
    roleDialogVisible.value = false
    fetchUsers()
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '操作失败')
  }
}

// 启用/禁用
async function handleToggle(row) {
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确认${action}用户「${row.username}」？`, '提示', { type: 'warning' })
    await request.put(`/api/users/${row.id}/status`, { is_active: !row.is_active })
    ElMessage.success(`${action}成功`)
    fetchUsers()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(err?.response?.data?.message || '操作失败')
  }
}

// 重置密码
function showResetDialog(row) {
  currentUser.value = row
  newPassword.value = ''
  resetDialogVisible.value = true
}
async function handleResetConfirm() {
  try {
    const res = await request.put(`/api/users/${currentUser.value.id}/reset-password`, {
      new_password: newPassword.value || undefined
    })
    const pwd = res?.new_password || '（随机生成）'
    ElMessage.success(`密码已重置，新密码：${pwd}`)
    resetDialogVisible.value = false
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || '操作失败')
  }
}

// 删除用户
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除用户「${row.username}」？此操作不可恢复。`, '提示', { type: 'warning' })
    await request.delete(`/api/users/${row.id}`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error(err?.response?.data?.message || '操作失败')
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
