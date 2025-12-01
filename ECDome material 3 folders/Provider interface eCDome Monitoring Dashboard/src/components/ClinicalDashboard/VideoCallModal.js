import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Video, 
  VideoOff, 
  Mic, 
  MicOff, 
  Phone, 
  PhoneOff, 
  Monitor, 
  Users,
  MessageSquare,
  FileText,
  Settings
} from 'lucide-react';
import toast from 'react-hot-toast';

const VideoCallModal = ({ isOpen, onClose, patientData }) => {
  const [isCallActive, setIsCallActive] = useState(false);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [isConnecting, setIsConnecting] = useState(false);

  // Timer for call duration
  useEffect(() => {
    let interval;
    if (isCallActive) {
      interval = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    } else {
      setCallDuration(0);
    }
    return () => clearInterval(interval);
  }, [isCallActive]);

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartCall = () => {
    setIsConnecting(true);
    toast.success(`📞 Connecting to ${patientData?.name}...`);
    
    setTimeout(() => {
      setIsConnecting(false);
      setIsCallActive(true);
      toast.success(`✅ Connected to ${patientData?.name}`, {
        icon: '📞'
      });
    }, 2000);
  };

  const handleEndCall = () => {
    setIsCallActive(false);
    setCallDuration(0);
    toast.success(`Call ended - Duration: ${formatDuration(callDuration)}`);
    setTimeout(() => {
      onClose();
    }, 1000);
  };

  const toggleVideo = () => {
    setVideoEnabled(!videoEnabled);
    toast.success(videoEnabled ? 'Video disabled' : 'Video enabled', {
      icon: videoEnabled ? '📹' : '✅'
    });
  };

  const toggleAudio = () => {
    setAudioEnabled(!audioEnabled);
    toast.success(audioEnabled ? 'Microphone muted' : 'Microphone unmuted', {
      icon: audioEnabled ? '🔇' : '🎤'
    });
  };

  const toggleScreenShare = () => {
    setIsScreenSharing(!isScreenSharing);
    toast.success(isScreenSharing ? 'Screen sharing stopped' : 'Screen sharing started', {
      icon: '🖥️'
    });
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black bg-opacity-75"
          onClick={!isCallActive ? onClose : undefined}
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="relative w-full max-w-6xl max-h-[95vh] mx-4 bg-gray-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
        >
          {/* Header */}
          <div className="bg-gray-800 px-6 py-4 flex items-center justify-between border-b border-gray-700 flex-shrink-0">
            <div className="flex items-center space-x-4">
              <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Video className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">
                  {isCallActive ? `Video Call with ${patientData?.name}` : 'Start Video Call'}
                </h3>
                <div className="flex items-center space-x-3 text-sm">
                  {isCallActive ? (
                    <>
                      <span className="flex items-center space-x-1 text-green-400">
                        <div className="h-2 w-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span>Connected</span>
                      </span>
                      <span className="text-gray-400">•</span>
                      <span className="text-gray-300">{formatDuration(callDuration)}</span>
                    </>
                  ) : (
                    <span className="text-gray-400">
                      Patient ID: {patientData?.id}
                    </span>
                  )}
                </div>
              </div>
            </div>
            {!isCallActive && !isConnecting && (
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            )}
          </div>

          {/* Video Area */}
          <div className="bg-gray-900 relative flex-1 overflow-hidden">
            {!isCallActive ? (
              // Pre-call screen
              <div className="h-full flex flex-col items-center justify-center p-8">
                <div className="h-32 w-32 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-6">
                  <Users className="h-16 w-16 text-white" />
                </div>
                <h4 className="text-2xl font-semibold text-white mb-2">
                  {patientData?.name}
                </h4>
                <p className="text-gray-400 mb-2">
                  Age: {patientData?.age} • {patientData?.gender}
                </p>
                <p className="text-gray-500 mb-6">
                  Provider: {patientData?.provider}
                </p>
                
                {isConnecting ? (
                  <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mb-4"></div>
                    <p className="text-white">Connecting...</p>
                  </div>
                ) : (
                  <button
                    onClick={handleStartCall}
                    className="flex items-center space-x-3 px-8 py-4 bg-green-600 hover:bg-green-700 text-white rounded-xl font-medium transition-colors"
                  >
                    <Phone className="h-6 w-6" />
                    <span>Start Call</span>
                  </button>
                )}
              </div>
            ) : (
              // Active call screen
              <div className="h-full relative">
                {/* Main video feed */}
                <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
                  {videoEnabled ? (
                    <div className="text-center">
                      <div className="h-48 w-48 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4 mx-auto">
                        <Users className="h-24 w-24 text-white" />
                      </div>
                      <p className="text-white text-xl">{patientData?.name}</p>
                      <p className="text-gray-400">Video Feed Active</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <VideoOff className="h-24 w-24 text-gray-500 mx-auto mb-4" />
                      <p className="text-gray-400">Video is off</p>
                    </div>
                  )}
                </div>

                {/* Screen sharing indicator */}
                {isScreenSharing && (
                  <div className="absolute top-4 left-4 bg-yellow-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
                    <Monitor className="h-4 w-4" />
                    <span className="text-sm font-medium">Screen Sharing</span>
                  </div>
                )}

                {/* Picture-in-picture (self view) */}
                <div className="absolute bottom-20 right-4 w-48 aspect-video bg-gray-700 rounded-lg shadow-2xl overflow-hidden border-2 border-gray-600">
                  <div className="w-full h-full flex items-center justify-center">
                    {videoEnabled ? (
                      <div className="text-center">
                        <Video className="h-8 w-8 text-gray-400 mx-auto mb-1" />
                        <p className="text-xs text-gray-400">You</p>
                      </div>
                    ) : (
                      <div className="text-center">
                        <VideoOff className="h-8 w-8 text-gray-500 mx-auto mb-1" />
                        <p className="text-xs text-gray-500">Camera Off</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Controls */}
          {isCallActive && (
            <div className="bg-gray-800 px-6 py-4 border-t border-gray-700 flex-shrink-0">
              <div className="flex items-center justify-center space-x-4">
                {/* Video Toggle */}
                <button
                  onClick={toggleVideo}
                  className={`p-4 rounded-full transition-colors ${
                    videoEnabled
                      ? 'bg-gray-700 hover:bg-gray-600 text-white'
                      : 'bg-red-600 hover:bg-red-700 text-white'
                  }`}
                  title={videoEnabled ? 'Turn off camera' : 'Turn on camera'}
                >
                  {videoEnabled ? (
                    <Video className="h-6 w-6" />
                  ) : (
                    <VideoOff className="h-6 w-6" />
                  )}
                </button>

                {/* Audio Toggle */}
                <button
                  onClick={toggleAudio}
                  className={`p-4 rounded-full transition-colors ${
                    audioEnabled
                      ? 'bg-gray-700 hover:bg-gray-600 text-white'
                      : 'bg-red-600 hover:bg-red-700 text-white'
                  }`}
                  title={audioEnabled ? 'Mute microphone' : 'Unmute microphone'}
                >
                  {audioEnabled ? (
                    <Mic className="h-6 w-6" />
                  ) : (
                    <MicOff className="h-6 w-6" />
                  )}
                </button>

                {/* Screen Share */}
                <button
                  onClick={toggleScreenShare}
                  className={`p-4 rounded-full transition-colors ${
                    isScreenSharing
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'bg-gray-700 hover:bg-gray-600 text-white'
                  }`}
                  title={isScreenSharing ? 'Stop screen sharing' : 'Share screen'}
                >
                  <Monitor className="h-6 w-6" />
                </button>

                {/* Chat */}
                <button
                  className="p-4 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors"
                  title="Open chat"
                >
                  <MessageSquare className="h-6 w-6" />
                </button>

                {/* Notes */}
                <button
                  className="p-4 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors"
                  title="Clinical notes"
                >
                  <FileText className="h-6 w-6" />
                </button>

                {/* Settings */}
                <button
                  className="p-4 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors"
                  title="Settings"
                >
                  <Settings className="h-6 w-6" />
                </button>

                {/* End Call */}
                <button
                  onClick={handleEndCall}
                  className="p-4 rounded-full bg-red-600 hover:bg-red-700 text-white transition-colors ml-4"
                  title="End call"
                >
                  <PhoneOff className="h-6 w-6" />
                </button>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default VideoCallModal;

