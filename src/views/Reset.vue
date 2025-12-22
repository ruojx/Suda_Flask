<!-- /src/views/Reset.vue -->
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/userStore'
// import { resetByOldPwdApi } from '@/api/public' // 如已实现后端接口，取消注释

const router = useRouter()
const userStore = useUserStore()

// ====== 使用旧密码修改 ======
const formRef = ref()
const form = reactive({
  username: '',
  oldPassword: '',
  newPassword: '',
  confirmPwd: ''
})
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 32, message: '长度 6~32 个字符', trigger: 'blur' }
  ],
  confirmPwd: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_, v, cb) => {
        if (!v) return cb(new Error('请再次输入新密码'))
        if (v !== form.newPassword) return cb(new Error('两次输入的密码不一致'))
        cb()
      },
      trigger: 'blur'
    }
  ]
}

// 提交：旧密码修改
const submit = async () => {
  await formRef.value?.validate()
  try {
    // 若已接后端，请改为实际接口调用
    // const res = await resetByOldPwdApi({
    //   username: form.username,
    //   oldPassword: form.oldPassword,
    //   newPassword: form.newPassword
    // })
    // if (res?.code === 1) {
    //   ElMessage.success('密码修改成功，请重新登录')
    //   userStore.clearUser?.()
    //   window.dispatchEvent(new Event('auth:changed'))
    //   router.replace('/login')
    // } else {
    //   ElMessage.error(res?.msg || '修改失败')
    // }

    // 演示用本地分支（无后端）
    ElMessage.success('（演示）密码修改成功，请重新登录')
    userStore.clearUser?.()
    window.dispatchEvent(new Event('auth:changed'))
    router.replace('/login')
  } catch (e) {
    console.error(e)
    ElMessage.error('修改失败，请稍后重试')
  }
}

// 返回
const back = () => router.push('/login')
</script>

<template>
  <div id="container">
    <div class="reset-form page-transition">
      <p class="title">修改密码</p>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" clearable />
        </el-form-item>

        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="form.oldPassword" type="password" show-password placeholder="请输入旧密码" />
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="form.newPassword" type="password" show-password placeholder="请输入新密码（6~32位）" />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPwd">
          <el-input v-model="form.confirmPwd" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>

        <div class="button-group">
          <el-button class="btn back-btn" @click="back">返回</el-button>
          <el-button class="btn primary" type="primary" @click="submit">确认修改</el-button>
        </div>
      </el-form>

      <div class="hint">
        <span>忘记密码？请联系管理员协助重置。</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
#container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 12px;
  background-image: url("@/assets/login_bg.jpg");
}
.reset-form {
  width: 460px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #fff;
  padding: 28px 24px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.title {
  margin: 2px 0 18px;
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  color: #111;
}

/* 表单状态 */
.el-form-item {
  margin-bottom: 16px;
}

:deep(.el-form-item__label) {
  color: #444;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #d1d5db inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #9ca3af inset;
}

:deep(.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 2px #1e80ff inset;
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.btn {
  flex: 1;
  height: 40px;
  border-radius: 8px;
  font-size: 15px;
}

.primary {
  background: #1e80ff;
  border-color: #1e80ff;
  color: #fff;
}

.back-btn {
  background: #f5f7fa;
  color: #111;
  border-color: #e5e7eb;
}

.back-btn:hover {
  background: #e5e7eb;
}

/* 底部提示 */
.hint {
  text-align: center;
  margin-top: 12px;
  color: #6b7280;
  font-size: 13px;
}
</style>
