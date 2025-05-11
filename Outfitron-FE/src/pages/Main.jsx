import React, { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Main = () => {
  // const baseUrl = "https://curly-spork-pjrrp4jwj9r936vg-3000.app.github.dev";
  // const baseUrl = "http://localhost:3000"
  const baseUrl = "https://musical-funicular-g4qq7j4r467w29jxr-3000.app.github.dev"
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [selfiePreview, setSelfiePreview] = useState(null);
  const [fullBodyPreview, setFullBodyPreview] = useState(null);
  const [showCamera, setShowCamera] = useState(false);
  const [resultText, setResultText] = useState('');
  const [uploading, setUploading] = useState(false);
  const streamRef = useRef(null);

  const launchCamera = async () => {
    setShowCamera(true);
    if (navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        streamRef.current = stream;
        videoRef.current.srcObject = stream;
      } catch (err) {
        alert('Camera access denied: ' + err);
      }
    } else {
      alert('Camera not supported in this browser.');
    }
  };

  useEffect(() => {

    const token = localStorage.getItem('userToken');
    if(!token || token.length<5){
        navigate("/login");
    }

});

  const capturePhoto = () => {
    const ctx = canvasRef.current.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0, 640, 480);
    canvasRef.current.classList.remove('hidden');
    videoRef.current.classList.add('hidden');
  };

  const captureAgain = () => {
    canvasRef.current.classList.add('hidden');
    videoRef.current.classList.remove('hidden');
  };

  const handlePreview = (e, setter) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => setter(reader.result);
      reader.readAsDataURL(file);
    }
  };


  const submitImages = async () => {
    setUploading(true);
    setResultText('🔄 Please wait, uploading images...');
    const selfieInput = document.getElementById('selfieInput');
    const fullBodyInput = document.getElementById('fullBodyInput');
    const selfieFile = selfieInput.files[0];
    const fullBodyFile = fullBodyInput.files[0];

    if (!selfieFile || !fullBodyFile) {
      alert('Please upload both selfie and full body images.');
      setUploading(false);
      return;
    }

    const formData = new FormData();
    formData.append('selfie', selfieFile);
    formData.append('fullbody', fullBodyFile);

    try {

      const uploadResponse = await fetch(`${baseUrl}/upload`, {
        method: 'POST',
        headers : {
          'Authorization': `Bearer ${localStorage.getItem("userToken")}`
        },
        body: formData,
      });

      if(uploadResponse.status === 401){
        localStorage.clear();
        navigate("/login");
      }

      if (uploadResponse.ok) {
        setResultText('🔄 Please wait, analyzing images...');
        const outputResponse = await fetch(`${baseUrl}/output` , {
          method : 'GET',
          headers : {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem("userToken")}`
          }
        });

        if(uploadResponse.status === 401){
          localStorage.clear();
          navigate("/login");
        }
        
        const output = await outputResponse.text();
        setResultText(output);
      } else {
        setResultText('❌ Error uploading images. Try again.');
      }
    } catch (error) {
      setResultText('⚠️ Something went wrong: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen scroll-smooth">
      <div className="flex flex-col items-center justify-center text-center px-4 pt-40 pb-10 w-full">
        <h1 className="text-5xl md:text-7xl font-extrabold fancy-text glow">Outfitron</h1>
        <p className="text-lg md:text-xl mt-6 text-gray-300 max-w-2xl">
          Your AI-powered fashion companion. Outfitron analyzes your skin tone, body shape, and weather to recommend perfect outfits just for you. ✨
        </p>
        <p className="italic text-pink-400 mt-4 text-md md:text-lg">“Style isn’t just what you wear. It’s what fits *you*.”</p>

       

        <div className="mt-10 flex flex-col items-center gap-6 w-full">
          <div className="text-center w-full">
            <label className="block mb-2 text-sm text-gray-300 font-medium">Upload Selfie</label>
            <input id="selfieInput" type="file" accept="image/*" className="hidden" onChange={(e) => handlePreview(e, setSelfiePreview)} />
            <button onClick={() => document.getElementById('selfieInput').click()} className="mt-4 px-8 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-full shadow-lg hover:scale-105 transition transform duration-300">
              📷 Upload Selfie
            </button>
            {selfiePreview && <img src={selfiePreview} alt="Selfie Preview" className="mt-3 rounded-xl border-2 border-indigo-400 w-full max-w-xs mx-auto" />}
          </div>

          <div className="text-center w-full">
            <label className="block mb-2 text-sm text-gray-300 font-medium">Upload Full Body (Front)</label>
            <input id="fullBodyInput" type="file" accept="image/*" className="hidden" onChange={(e) => handlePreview(e, setFullBodyPreview)} />
            <button onClick={() => document.getElementById('fullBodyInput').click()} className="mt-4 px-8 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-full shadow-lg hover:scale-105 transition transform duration-300">
              🧍 Upload Full Body
            </button>
            {fullBodyPreview && <img src={fullBodyPreview} alt="Full Body Preview" className="mt-3 rounded-xl border-2 border-pink-400 w-full max-w-xs mx-auto" />}
          </div>
        </div>

        {showCamera && (
          <div className="mt-10 flex flex-col items-center space-y-4 w-full">
            <video ref={videoRef} width="640" height="480" autoPlay className="w-full max-w-3xl rounded-xl shadow-lg border-2 border-white"></video>
            <div className="flex space-x-4">
              <button onClick={capturePhoto} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow">📸 Capture Photo</button>
              <button onClick={captureAgain} className="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded shadow">🔄 Capture Again</button>
            </div>
            <canvas ref={canvasRef} width="640" height="480" className="hidden w-full max-w-3xl rounded-xl shadow-lg border-2 border-dashed border-green-400"></canvas>
          </div>
        )}

        <div className="mt-12 text-center w-full">
          <button onClick={submitImages} disabled={uploading} className={`px-10 py-3 font-bold rounded-full shadow transition duration-300 ${uploading ? 'bg-gray-500 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 text-white'}`}>
            {uploading ? '⏳ Uploading...' : '✅ Submit for Analysis'}
          </button>
          <p className="mt-6 text-lg text-yellow-400 font-mono whitespace-pre-wrap">{resultText}</p>
        </div>
      </div>

      <section id="about" className="bg-gray-800 py-16 px-6 w-full">
        <div className="w-full mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6 fancy-text">Why Outfitron?</h2>
          <p className="text-gray-300 text-lg leading-relaxed">
            Outfitron isn't just a styling app — it's a smart mirror that sees you, understands your natural tones, and empowers your confidence with the perfect outfit recommendations.
          </p>
          <p className="mt-4 text-purple-400 italic">"Be bold. Be you. Be dressed for every moment."</p>
        </div>
      </section>

      <section id="features" className="bg-gray-900 py-16 px-6 w-full">
        <div className="w-full mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6 fancy-text">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-10 text-left text-gray-300">
            <div className="bg-gray-800 p-6 rounded-xl shadow hover:shadow-xl transition">
              <h3 className="text-xl font-bold text-pink-400 mb-2">🖼️ Image Upload</h3>
              <p>Upload or snap a photo. Our system extracts skin tone, facial region, and body features using advanced image processing.</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-xl shadow hover:shadow-xl transition">
              <h3 className="text-xl font-bold text-yellow-400 mb-2">🧠 ML Analysis</h3>
              <p>We feed your features and live weather data into a custom-trained model to understand what's comfortable and stylish for your body type.</p>
            </div>
            <div className="bg-gray-800 p-6 rounded-xl shadow hover:shadow-xl transition">
              <h3 className="text-xl font-bold text-green-400 mb-2">👗 Outfit Suggestion</h3>
              <p>Outfitron gives you beautiful, seasonal outfit recommendations based on you — not generic trends.</p>
            </div>
          </div>
        </div>
      </section>

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

export default Main;
