import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router' 

//创建axios实例对象
const request = axios.create({
  baseURL: '/api',
  timeout: 600000
})
 
//request的请求拦截器,获取localStorage中的token，在请求头中添加token
request.interceptors.request.use(
  (config) => { //成功回调
    const loginUser = JSON.parse(localStorage.getItem('loginUser')) 
    if (loginUser && loginUser.token) {
      config.headers.token = loginUser.token //将token添加到请求头中
    }
    return config
  },
  (error) => { //失败回调
    return Promise.reject(error)
  }
)

//axios的响应 response 拦截器
request.interceptors.response.use(
  (response) => { //成功回调
    return response.data
  },
  (error) => { //失败回调
    if (error.response.status === 401) {
      ElMessage.error("登录超时，请重新登录");
      router.push("/login");
    }
    return Promise.reject(error)
  }
)
 
export default request