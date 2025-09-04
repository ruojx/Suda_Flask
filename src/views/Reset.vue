<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { resetApi } from '@/api/public'

const router = useRouter()
const route = useRoute()

const mode = ref(route.query.mode || 'modify')  // 默认修改密码
const role = ref(Number(route.query.role || ''))
const titleText = computed(() => {
  return mode.value === 'forget' ? '找回密码' : '修改密码'
})
const selectedRole = computed(() => {
  switch (role.value) {
    case 1:
      return 'student'
    case 2:
      return 'teacher'
    case 3:
      return 'admin'
  }
})
const roleLabel = computed(() => {
  switch (role.value) {
    case 1:
      return '学生'
    case 2:
      return '教工'
    case 3:
      return '管理员'
    default:
      return '用户'
  }
})
const loginUser = JSON.parse(localStorage.getItem('loginUser') || '{}')

// 表单数据，根据模式使用不同字段
const form = ref({
  id: loginUser.id,
  role: role.value,
  identifier: '',      // 忘记密码模式填写
  oldPassword: '',     // 修改密码模式填写
  newPassword: '',
  repeatPassword: ''
})

// 确认按钮逻辑
const sure = async () => {
  if (!form.value.newPassword || !form.value.repeatPassword) {
    ElMessage.error('新密码不能为空')
    return
  }

  if (form.value.newPassword !== form.value.repeatPassword) {
    ElMessage.error('两次密码不一致')
    return
  }

  if (mode.value === 'forget' && !form.value.identifier) {
    ElMessage.error(`请填写${roleLabel.value}号`)
    return
  }
  else if (mode.value === 'modify' && !form.value.oldPassword) {
    ElMessage.error('请输入原密码')
    return
  }
  const result = await resetApi(form.value);
  if (result.code) {
    ElMessage.success('密码重置成功')
  }
  else {
    ElMessage.error(`无法更新，请检查后重新操作`)
    if (mode.value === 'forget') {
      router.push('/')
    }
    else {
      router.push(`/${selectedRole.value}`)
    }
  }
}

// 返回按钮
const back = () => {
  router.back()
}
</script>

<template>
  <div id="container">
    <div class="reset-form page-transition">
      <el-form label-width="80px">
        <p class="title">{{ titleText }}</p>

        <el-form-item v-if="mode === 'forget'" :label="`${roleLabel}号`">
          <el-input v-model="form.identifier" :placeholder="`请输入${roleLabel}号`" />
        </el-form-item>

        <el-form-item v-if="mode === 'modify'" label="原密码">
          <el-input v-model="form.oldPassword" type="password" placeholder="请输入原密码" />
        </el-form-item>

        <el-form-item label="新密码">
          <el-input v-model="form.newPassword" type="password" placeholder="请输入新密码" />
        </el-form-item>

        <el-form-item label="确认密码">
          <el-input v-model="form.repeatPassword" type="password" placeholder="请再次输入新密码" />
        </el-form-item>

        <div class="button-group">
          <el-button class="reset-button back-btn" @click="back">返回</el-button>
          <el-button class="reset-button confirm-btn" type="primary" @click="sure">确认</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<!-- <style scoped>
#container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 90px 20px 20px 20px;
  width: 100%;
}

.reset-form {
  width: 370px;
  background: rgba(255,255,255,0.92);
  padding: 36px 32px 28px 32px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.13);
  position: relative;
  backdrop-filter: blur(6px);
  margin-top: 90px;
}

.page-transition {
  animation: page-fade-in 0.7s cubic-bezier(.4,0,.2,1);
}

@keyframes page-fade-in {
  0% { opacity: 0; transform: translateY(40px) scale(0.98); }
  100% { opacity: 1; transform: none; }
}

@keyframes card-fade-in {
  0% { opacity: 0; transform: translateY(40px) scale(0.98); }
  100% { opacity: 1; transform: none; }
}

.title {
  text-align: center;
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--student-color);
  letter-spacing: 0.04em;
}

.el-form-item {
  margin-bottom: 18px;
}

.button-group {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-top: 24px;
}

.reset-button {
  flex: 1;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
  padding: 12px 24px;
}

.back-btn {
  background: #f5f5f5;
  color: #666;
}

.back-btn:hover {
  background: #e8e8e8;
  transform: translateY(-1px);
}

.confirm-btn {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  color: #fff;
}

.confirm-btn:hover {
  background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%);
  transform: translateY(-1px);
}
</style> -->

<style scoped>
#container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 90px 20px 20px 20px;
  width: 100%;
}

.reset-form {
  width: 370px;
  background: #fff;
  padding: 36px 32px 28px 32px;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  position: relative;
  margin-top: 90px;
}

.page-transition {
  animation: page-fade-in 0.7s cubic-bezier(.4,0,.2,1);
}

@keyframes page-fade-in {
  0% { opacity: 0; transform: translateY(40px) scale(0.98); }
  100% { opacity: 1; transform: none; }
}

.title {
  text-align: center;
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 24px;
  color: #333;
  letter-spacing: 0.04em;
}

.el-form-item {
  margin-bottom: 18px;
}

.button-group {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-top: 24px;
}

.reset-button {
  flex: 1;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
  padding: 12px 24px;
}

.back-btn {
  background: #f0f0f0;
  color: #666;
}

.back-btn:hover {
  background: #e0e0e0;
  transform: translateY(-1px);
}

.confirm-btn {
  background: #333;
  color: #fff;
}

.confirm-btn:hover {
  background: #444;
  transform: translateY(-1px);
}
</style>
