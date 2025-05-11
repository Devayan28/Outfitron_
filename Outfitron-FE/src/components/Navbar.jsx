
const Navbar = () => {

  const callChathelper = () => {
  window.location.href = "https://chatapp-ed5s8m9esd2dcqrqthkisc.streamlit.app/";
}

    return (
        <>
            <nav className="w-full bg-gray-800 shadow-md fixed top-0 left-0 z-50 shadow-[0_4px_12px_rgba(255,255,255,0.8)] rounded-lg">
        <div className="w-full px-4 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold fancy-text">Outfitron</h2>
          <div className="space-x-6 text-gray-300 text-sm md:text-base">
            <a href="/" className="hover:text-white transition">Home</a>
            <a href="#about" className="hover:text-white transition">About</a>
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="/login" className="hover:text-white transition">Login</a>
            <a href="/signin"  className="hover:text-white transition">SignIn</a>
            {/* <a href=`${chatHelper}`  className="hover:text-white transition">SignIn</a> */}
            <button onClick={callChathelper}>ChatHelper</button>
          </div>
        </div>
      </nav>
        </>
    );
}

export default Navbar;