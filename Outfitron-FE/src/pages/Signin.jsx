import React, { useState , useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendOTP, signUp } from '../api';

const Signin = () => {
    const navigate = useNavigate();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [otp , setOtp] = useState('');
    const [name , setName] = useState('');

    useEffect(() => {
        localStorage.clear();
    },[]);

    const onSubmitHandler = async() => {
        
        try{

            const user = await signUp({name , email , password , otp});
            if (user) {
                navigate('/login');
            }

        }catch(err){
            console.log(err);
        }

    }

    const inOtpSubmitHandler = async() => {

        try{

            const otp = await sendOTP(email);
            if (otp) {
                console.log("OTP sent successfully");
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

    const onChangeOtpHandler = (e) => {
        setOtp(e.target.value);
    }

    const onChangeNameHandler = (e) => {
        setName(e.target.value);
    }

    return (
        <div className="min-h-screen w-[60rem] bg-gray-900 text-white flex items-center justify-center py-12 px-4">
  <div className="bg-gray-800 p-8 rounded-xl shadow-lg w-full max-w-xl">
    <h3 className="text-3xl font-bold text-center mb-6 fancy-text glow">Sign In</h3>

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

      <button
        onClick={inOtpSubmitHandler}
        className="w-full py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-full shadow-md hover:scale-105 transform transition duration-300"
      >
        📩 Send OTP to Mail
      </button>

      <div>
        <label htmlFor="otp" className="block mb-2 text-sm font-medium text-gray-300">OTP</label>
        <input
          type="text"
          name="otp"
          onChange={onChangeOtpHandler}
          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
        />
      </div>

      <div>
        <label htmlFor="name" className="block mb-2 text-sm font-medium text-gray-300">Name</label>
        <input
          type="text"
          name="name"
          onChange={onChangeNameHandler}
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
        🔐 Sign In
      </button>
    </div>
  </div>

  {/* Reusable Theme Styles */}
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

export default Signin;
