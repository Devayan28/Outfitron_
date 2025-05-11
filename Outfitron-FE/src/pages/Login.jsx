import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import  { login } from "../api"; 

const Login = () => {
    const navigate = useNavigate();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const onSubmitHandler = async() => {
        
        try{

            const user = await login({email , password});
            if (user) {
                // console.log(user.data)
                localStorage.clear();
                localStorage.setItem('userToken' , user.data.token)
                navigate('/');
            }

        }catch(err){
            console.log(err);
        }

    }

    const onChangeEmailHandler = (e) => {
        setEmail(e.target.value);
    }

    const onChangePasswordHandler = (e) => {
        setPassword(e.target.value);
    }

    const routeHandler = () => {
        navigate("/signin");
    }

    return (
       
        <div className="min-h-screen w-[60rem] bg-gray-900 text-white flex items-center justify-center py-12 px-4">
  <div className="bg-gray-800 p-8 rounded-xl shadow-lg w-full max-w-xl">
    <h3 className="text-3xl font-bold text-center mb-6 fancy-text glow">Login</h3>

    <div className="space-y-6">
      <div>
        <label htmlFor="email" className="block mb-2 text-sm font-medium text-gray-300">Email</label>
        <input
          type="text"
          name="email"
          onChange={onChangeEmailHandler}
          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
        />
      </div>

      <div>
        <label htmlFor="password" className="block mb-2 text-sm font-medium text-gray-300">Password</label>
        <input
          type="password"
          name="password"
          onChange={onChangePasswordHandler}
          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
        />
      </div>

      <button
        onClick={onSubmitHandler}
        className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold rounded-full shadow-lg hover:scale-105 transform transition duration-300"
      >
        🔐 Submit
      </button>
      <button
        onClick={routeHandler}
        className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold rounded-full shadow-lg hover:scale-105 transform transition duration-300"
      >
        Dont have an account , Sign in first.
      </button>
    </div>
  </div>

  {/* Theme Reuse Styles */}
  <style jsx>{`
    .fancy-text {
      background: linear-gradient(90deg, #00f260, #0575e6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    @keyframes pulse-grow {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }

    .glow {
      animation: pulse-grow 3s infinite;
    }
  `}</style>
</div>

    );
};

export default Login;
