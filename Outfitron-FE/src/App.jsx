import './App.css'
import {BrowserRouter , Routes,Route, Navigate} from 'react-router-dom'
import Main from './pages/Main'
import Login from './pages/Login'
import Signin from './pages/Signin'
import Navbar from './components/Navbar'


function App() {


  // const GoogleAuthWrapper = () =>{ 
  //   return(
  //     <GoogleOAuthProvider clientId={import.meta.env.VITE_CLIENT_ID}>
  //       <GoogleLogin></GoogleLogin>
  //     </GoogleOAuthProvider>
  //   )
  // }


  return (
    
    <BrowserRouter>
    <Navbar/>
    <Routes>
      {/*
      <Route path = '/signup' element={<GoogleLogin/>}/>
      <Route path ='/google-login-signup' element={<GoogleLogin/>}/>
      */}
      <Route path= '/' element={<Main/>}/>
      <Route path= '/login' element={<Login/>}/>
      <Route path= '/signin' element={<Signin/>}/>
      {/* <Route path='/login' element={<Login/>}/>
      <Route path='/signin' element={<SignUp/>}/>
      <Route path= '/user' element={<UserPage/>}/>
      <Route path= '/payment' element={<Payment/>}/>
      <Route path= '/forgot-password' element={<ForgotPassword/>}/>
      <Route path= '/update-password/:token' element={<ResetPassword/>}/> */}
    </Routes>
    </BrowserRouter>
    
  )
}


export default App