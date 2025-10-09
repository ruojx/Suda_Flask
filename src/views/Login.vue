<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { loginApi } from '@/api/public'
import { useUserStore } from '@/stores/userStore' // 引入 userStore

const router = useRouter()
const userStore = useUserStore() // 获取 Pinia store 实例

// 登录表单数据
const loginForm = reactive({
  username: '1',
  password: '1'
})

// 登录处理
const login = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  try {
    const result = await loginApi({
      username: loginForm.username,
      password: loginForm.password,
    })

    if (result.code === 1) {
      // 保存用户信息到 Pinia 和 localStorage
      userStore.setUser(result.data)
      // 通知同页的 Layout 立刻刷新认证态
      window.dispatchEvent(new Event('auth:changed'))
      // 跳转
      router.replace('/home')

      // 记录用户登录日志（直接调用后端接口）
      try {
        // 这里可以调用后端接口记录登录日志
        // await recordUserLoginApi(result.data.id)
        console.log('用户登录成功')
      } catch (error) {
        console.error('记录用户登录日志失败:', error)
      }

      // 跳转至对应角色页面
      router.push(`/home`)
    } else {
      ElMessage.error('用户或密码不正确')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请稍后重试')
  }
}

// 返回入口界面
const back = () => {
  loginForm.username = ''
  loginForm.password = ''
  router.push(`/home`)
}

// 忘记密码
const reset = () => {
  router.push(`/reset?mode=forget&role=${role.value}`)
}
</script>


<template>
  <div id="container">
    <div class="login-form page-transition">
      <el-form label-width="80px">
        <p class="title">用户登录</p>
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input type="password" v-model="loginForm.password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <div class="button-group">
          <el-button class="login-button back-btn" type="primary" @click="back">返回</el-button>
          <!-- <el-button class="login-button forgot-btn" type="primary" @click="reset">忘记密码</el-button> -->
          <el-button class="login-button login-btn" type="primary" @click="login">登录</el-button>
        </div>
        <div class="register-link">
          <span>还没有账号？请联系相关负责人</span>
        </div>
      </el-form>
    </div>
  </div>
</template>


<style scoped>
/* 整体容器：竖向居中 */
#container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 12px;
  background-image: url("@/assets/login_bg.jpg");
}

/* 登录卡片：竖向偏长 */
.login-form {
  width: 360px; /* 固定宽度，避免横向铺开 */
  min-height: 300px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #fff;
  padding: 32px 28px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
  border: auto auto;
  display: flex;
  flex-direction: column;
  justify-content: center; /* 内容垂直居中，无底部留白 */
}

/* 标题 */
.title {
  margin: 0 0 24px;
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  color: #111;
}

/* 表单项 */
.el-form-item {
  margin-bottom: 18px;
}
:deep(.el-form-item__label) {
  color: #444;
}

/* 输入框：选中时边框高亮 */
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

/* 按钮组：横排等宽 */
.button-group {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
.login-button {
  flex: 1; /* 两个按钮等宽 */
  height: 40px;
  border-radius: 8px;
  font-size: 15px;
}
.login-btn {
  background: #1e80ff;
  border-color: #1e80ff;
}
.login-btn:hover {
  background: #0b5ed7;
  border-color: #0b5ed7;
}
.back-btn {
  background: #f5f7fa;
  color: #111;
  border-color: #e5e7eb;
}
.back-btn:hover {
  background: #e5e7eb;
}

/* 注册提示 */
.register-link {
  text-align: center;
  margin-top: 16px;
  color: #6b7280;
  font-size: 13px;
}
</style>

