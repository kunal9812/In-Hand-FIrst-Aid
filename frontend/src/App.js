import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Emergency Categories
const EMERGENCY_TYPES = {
  choking: {
    name: 'Choking',
    icon: '🫁',
    color: 'bg-red-500',
    description: 'Cannot breathe, cough, or speak'
  },
  bleeding: {
    name: 'Bleeding',
    icon: '🩸',
    color: 'bg-red-600',
    description: 'Heavy bleeding from cuts or wounds'
  },
  allergic_reaction: {
    name: 'Allergic Reaction',
    icon: '⚠️',
    color: 'bg-orange-500',
    description: 'Severe allergic reaction symptoms'
  }
};

// Voice synthesis hook
const useSpeechSynthesis = () => {
  const [speaking, setSpeaking] = useState(false);
  const [supported, setSupported] = useState(false);

  useEffect(() => {
    setSupported('speechSynthesis' in window);
  }, []);

  const speak = (text, options = {}) => {
    if (!supported) {
      console.warn('Speech synthesis not supported');
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Configure voice settings
    utterance.rate = options.rate || 0.9;
    utterance.pitch = options.pitch || 1;
    utterance.volume = options.volume || 1;

    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stop = () => {
    window.speechSynthesis.cancel();
    setSpeaking(false);
  };

  return { speak, stop, speaking, supported };
};

// Emergency Category Card Component
const EmergencyCard = ({ type, emergency, onSelect }) => (
  <div 
    className={`${emergency.color} rounded-lg p-6 text-white cursor-pointer transform transition-transform hover:scale-105 shadow-lg`}
    onClick={() => onSelect(type)}
  >
    <div className="text-4xl mb-4">{emergency.icon}</div>
    <h3 className="text-xl font-bold mb-2">{emergency.name}</h3>
    <p className="text-sm opacity-90">{emergency.description}</p>
  </div>
);

// Emergency Instructions Component
const EmergencyInstructions = ({ instructions, onBack }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedInstruction, setSelectedInstruction] = useState(null);
  const { speak, stop, speaking, supported } = useSpeechSynthesis();

  useEffect(() => {
    if (instructions.length > 0 && !selectedInstruction) {
      setSelectedInstruction(instructions[0]);
    }
  }, [instructions, selectedInstruction]);

  const speakStep = (stepIndex) => {
    if (selectedInstruction && selectedInstruction.voice_instructions[stepIndex]) {
      speak(selectedInstruction.voice_instructions[stepIndex]);
    }
  };

  const speakAllSteps = () => {
    if (!selectedInstruction) return;
    
    const allText = selectedInstruction.voice_instructions.join('. ');
    speak(`Emergency instructions for ${selectedInstruction.title}. ${allText}`);
  };

  const nextStep = () => {
    if (selectedInstruction && currentStep < selectedInstruction.steps.length - 1) {
      const nextIndex = currentStep + 1;
      setCurrentStep(nextIndex);
      speakStep(nextIndex);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      const prevIndex = currentStep - 1;
      setCurrentStep(prevIndex);
      speakStep(prevIndex);
    }
  };

  if (!selectedInstruction) {
    return (
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-red-500 mx-auto mb-4"></div>
        <p>Loading emergency instructions...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-red-600 text-white p-6 rounded-t-lg">
        <button 
          onClick={onBack}
          className="mb-4 text-red-200 hover:text-white"
        >
          ← Back to Emergencies
        </button>
        <h2 className="text-2xl font-bold mb-2">{selectedInstruction.title}</h2>
        <p className="text-red-100 mb-2">{selectedInstruction.description}</p>
        <div className="flex flex-wrap gap-4 text-sm">
          <span className="bg-red-700 px-3 py-1 rounded">
            Severity: {selectedInstruction.severity.toUpperCase()}
          </span>
          <span className="bg-red-700 px-3 py-1 rounded">
            Duration: {selectedInstruction.duration_estimate}
          </span>
        </div>
      </div>

      {/* Instruction Selection */}
      {instructions.length > 1 && (
        <div className="bg-gray-100 p-4">
          <h3 className="font-semibold mb-2">Choose specific scenario:</h3>
          <div className="flex flex-wrap gap-2">
            {instructions.map((instruction, index) => (
              <button
                key={index}
                onClick={() => {
                  setSelectedInstruction(instruction);
                  setCurrentStep(0);
                }}
                className={`px-4 py-2 rounded ${
                  selectedInstruction.id === instruction.id 
                    ? 'bg-red-500 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-200'
                }`}
              >
                {instruction.title}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Instructions */}
      <div className="bg-white p-6 shadow-lg">
        {/* Emergency Call Warning */}
        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-6">
          <div className="flex">
            <div className="text-yellow-600 text-xl mr-3">⚠️</div>
            <div>
              <h4 className="font-bold text-yellow-800">When to call 911:</h4>
              <p className="text-yellow-700">{selectedInstruction.when_to_call_911}</p>
            </div>
          </div>
        </div>

        {/* Voice Controls */}
        <div className="flex flex-wrap gap-4 mb-6">
          <button
            onClick={speakAllSteps}
            disabled={speaking}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold flex items-center"
          >
            🔊 {speaking ? 'Speaking...' : 'Speak All Steps'}
          </button>
          <button
            onClick={stop}
            className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold"
          >
            ⏹️ Stop
          </button>
          {!supported && (
            <div className="text-red-500 text-sm">
              ⚠️ Voice synthesis not supported on this device
            </div>
          )}
        </div>

        {/* Step Navigation */}
        <div className="flex justify-between items-center mb-6">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className="bg-gray-300 hover:bg-gray-400 disabled:bg-gray-200 disabled:text-gray-400 px-4 py-2 rounded"
          >
            ← Previous
          </button>
          <span className="text-lg font-semibold">
            Step {currentStep + 1} of {selectedInstruction.steps.length}
          </span>
          <button
            onClick={nextStep}
            disabled={currentStep === selectedInstruction.steps.length - 1}
            className="bg-gray-300 hover:bg-gray-400 disabled:bg-gray-200 disabled:text-gray-400 px-4 py-2 rounded"
          >
            Next →
          </button>
        </div>

        {/* Current Step */}
        <div className="text-center">
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-8 mb-4">
            <div className="text-6xl mb-4">{currentStep + 1}</div>
            <h3 className="text-2xl font-bold mb-4 text-red-800">
              {selectedInstruction.steps[currentStep]}
            </h3>
            <button
              onClick={() => speakStep(currentStep)}
              disabled={speaking}
              className="bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg"
            >
              🔊 Speak This Step
            </button>
          </div>
        </div>

        {/* All Steps Overview */}
        <div className="mt-8 bg-gray-50 p-6 rounded-lg">
          <h4 className="font-bold mb-4">All Steps:</h4>
          <ol className="list-decimal list-inside space-y-2">
            {selectedInstruction.steps.map((step, index) => (
              <li 
                key={index} 
                className={`cursor-pointer p-2 rounded ${
                  index === currentStep ? 'bg-red-100 font-semibold' : 'hover:bg-gray-100'
                }`}
                onClick={() => setCurrentStep(index)}
              >
                {step}
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
};

// Help Request Component
const HelpRequest = ({ onBack }) => {
  const [formData, setFormData] = useState({
    emergency_type: 'choking',
    location_description: '',
    contact_phone: '',
    additional_info: ''
  });
  const [location, setLocation] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    // Get user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => console.warn('Location access denied:', error)
      );
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const requestData = {
        ...formData,
        ...(location && { 
          latitude: location.latitude, 
          longitude: location.longitude 
        })
      };

      await axios.post(`${API}/help-requests`, requestData);
      setSubmitted(true);
    } catch (error) {
      console.error('Failed to submit help request:', error);
      alert('Failed to submit help request. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="bg-green-100 border border-green-400 text-green-700 px-6 py-8 rounded-lg">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold mb-4">Help Request Submitted</h2>
          <p className="mb-6">Your emergency help request has been sent. Someone will respond as soon as possible.</p>
          <div className="space-y-2">
            <p className="font-semibold">Important:</p>
            <p>• If this is life-threatening, call 911 immediately</p>
            <p>• Stay in a safe location if possible</p>
            <p>• Keep your phone available for contact</p>
          </div>
          <button 
            onClick={onBack}
            className="mt-6 bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
          >
            Back to Main Menu
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-orange-600 text-white p-6 rounded-t-lg">
        <button 
          onClick={onBack}
          className="mb-4 text-orange-200 hover:text-white"
        >
          ← Back to Main Menu
        </button>
        <h2 className="text-2xl font-bold">Request Emergency Help</h2>
        <p className="text-orange-100 mt-2">Fill out this form to request immediate assistance</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-6 shadow-lg">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type of Emergency *
            </label>
            <select
              value={formData.emergency_type}
              onChange={(e) => setFormData({...formData, emergency_type: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              required
            >
              <option value="choking">Choking</option>
              <option value="bleeding">Bleeding</option>
              <option value="allergic_reaction">Allergic Reaction</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location Description *
            </label>
            <input
              type="text"
              value={formData.location_description}
              onChange={(e) => setFormData({...formData, location_description: e.target.value})}
              placeholder="e.g., 123 Main St, Apartment 4B, or Restaurant near Central Park"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              required
            />
            {location && (
              <p className="text-sm text-green-600 mt-1">
                ✓ GPS coordinates will be included automatically
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contact Phone
            </label>
            <input
              type="tel"
              value={formData.contact_phone}
              onChange={(e) => setFormData({...formData, contact_phone: e.target.value})}
              placeholder="Your phone number"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Information
            </label>
            <textarea
              value={formData.additional_info}
              onChange={(e) => setFormData({...formData, additional_info: e.target.value})}
              placeholder="Any additional details that might help responders"
              rows={4}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-semibold mb-2">⚠️ Emergency Warning:</p>
            <p className="text-red-700 text-sm">
              If this is a life-threatening emergency, call 911 immediately. 
              This form is for requesting community assistance and may not provide immediate response.
            </p>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white py-4 px-6 rounded-lg font-semibold text-lg"
          >
            {submitting ? 'Sending Help Request...' : 'Send Help Request'}
          </button>
        </div>
      </form>
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('home');
  const [instructions, setInstructions] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleEmergencySelect = async (emergencyType) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/emergency-instructions/${emergencyType}`);
      setInstructions(response.data);
      setCurrentView('instructions');
    } catch (error) {
      console.error('Failed to load instructions:', error);
      alert('Failed to load emergency instructions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-red-500 mx-auto mb-4"></div>
          <p className="text-xl">Loading emergency instructions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-red-600 text-white p-6 shadow-lg">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold flex items-center">
            🚨 Emergency First Aid Assistant
          </h1>
          <p className="text-red-100 mt-2">Voice-guided emergency instructions that work offline</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto p-6">
        {currentView === 'home' && (
          <>
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-4">Select Your Emergency</h2>
              <p className="text-gray-600">Choose the emergency type for voice-guided instructions</p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-8">
              {Object.entries(EMERGENCY_TYPES).map(([type, emergency]) => (
                <EmergencyCard
                  key={type}
                  type={type}
                  emergency={emergency}
                  onSelect={handleEmergencySelect}
                />
              ))}
            </div>

            <div className="text-center">
              <button
                onClick={() => setCurrentView('help-request')}
                className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-4 rounded-lg font-semibold text-lg"
              >
                📞 Request Help from Community
              </button>
            </div>

            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-bold text-blue-800 mb-2">📱 Works Offline</h3>
              <p className="text-blue-700 text-sm">
                These instructions are cached on your device and work without internet connection. 
                Voice guidance is available on supported devices.
              </p>
            </div>
          </>
        )}

        {currentView === 'instructions' && (
          <EmergencyInstructions
            instructions={instructions}
            onBack={() => setCurrentView('home')}
          />
        )}

        {currentView === 'help-request' && (
          <HelpRequest onBack={() => setCurrentView('home')} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white p-6 mt-12">
        <div className="max-w-6xl mx-auto text-center">
          <p className="mb-2">⚠️ This app provides basic first aid guidance only</p>
          <p className="text-gray-300 text-sm">
            Always call 911 for life-threatening emergencies. This information is not a substitute for professional medical care.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;