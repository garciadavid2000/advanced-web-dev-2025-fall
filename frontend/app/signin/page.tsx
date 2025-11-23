'use client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export default function SignInPage() {
  const handleSignIn = () => {
    // Redirect to backend login endpoint
    window.location.href = `${API_BASE_URL}/auth/login`;
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-6 text-gray-800">Task Manager</h1>
        <p className="text-lg text-gray-600 mb-8">Sign in to manage your tasks</p>
        <button
          onClick={handleSignIn}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded transition duration-200"
        >
          Sign In with Google
        </button>
      </div>
    </div>
  );
}

