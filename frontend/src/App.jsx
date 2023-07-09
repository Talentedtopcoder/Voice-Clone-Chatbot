import React, { useEffect, useState } from "react";
import { Configuration, OpenAIApi } from "openai";
import "regenerator-runtime/runtime";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import { AiFillAudio, AiOutlineSend } from "react-icons/ai";
import { CiPlay1 } from "react-icons/ci";
import { SiAudiomack } from "react-icons/si";
import { FaRobot, FaUser } from "react-icons/fa";
import { useSpeechSynthesis } from "react-speech-kit";

const configuration = new Configuration({
  organization: "org-wPUPKj8xm113rDitqV5JzHha",
  apiKey: "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",
});
const openai = new OpenAIApi(configuration);
var audioPlayer = new Audio();

function App() {
  const [message, setMessage] = useState("");
  const [chats, setChats] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [voiceIds, setVoiceIds] = useState([]);
  const [voiceId, setVoiceId] = useState();

  const [playing, setPlaying] = useState(false);

  audioPlayer.onended = (ev) => {
    setPlaying(false);
  };

  audioPlayer.onpause = (ev) => {
    setPlaying(false);
  };

  audioPlayer.onplaying = (ev) => {
    setPlaying(true);
  };

  useEffect(() => {
    fetch(`${import.meta.env.VITE_ELEVEN_LAB_API_ROOT}/v1/voices`, {
      method: "GET",
      headers: {
        "xi-api-key": import.meta.env.VITE_ELEVEN_LAB_API_KEY,
      },
    }).then(async (res) => {
      const data = await res.json();

      setVoiceIds(
        data.voices.map((voice) => ({
          id: voice.voice_id,
          name: voice.name,
        }))
      );

      setVoiceId(data.voices[0].voice_id);
    });
  }, []);

  const stopSpeech = () => {
    audioPlayer.pause();
  };

  const playTextToSpeech = (url) => {
    audioPlayer.src = url;
    audioPlayer.play();
  };

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser doesn't support speech recognition.</span>;
  }

  const chat = async (e, message) => {
    e.preventDefault();

    setIsTyping(true);

    let msgs = chats;
    msgs.push({ role: "user", content: message });
    setChats(msgs);

    scrollTo(0, 1e10);
    setMessage("");

    await openai
      .createChatCompletion({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: "You are ChatGPT. You help with content writing.",
          },
          ...chats.map((chat) => ({
            role: chat.role,
            content: chat.content,
          })),
        ],
      })
      .then((result) => {
        if (voiceId) {
          fetch(
            `${
              import.meta.env.VITE_ELEVEN_LAB_API_ROOT
            }/v1/text-to-speech/${voiceId}?optimize_streaming_latency=0`,
            {
              method: "POST",
              headers: {
                "xi-api-key": import.meta.env.VITE_ELEVEN_LAB_API_KEY,
                accept: "audio/mpeg",
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                text: result.data.choices[0].message.content,
                model_id: "eleven_monolingual_v1",
                voice_settings: {
                  stability: 0,
                  similarity_boost: 0,
                },
              }),
            }
          ).then(async (res) => {
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);

            msgs.push({
              ...result.data.choices[0].message,
              url,
            });
            setChats(msgs);
            setIsTyping(false);
            scrollTo(0, 1e10);
          });
        } else {
          console.log("Voice ID is not selected.");
        }
      })
      .catch((error) => console.log(error));
  };

  useEffect(() => {
    if (transcript && transcript.length > 0) {
      setMessage(transcript);
    }
  }, [transcript]);

  const handleStart = (e) => {
    e.preventDefault();
    SpeechRecognition.startListening();
  };

  const handleStop = (e) => {
    e.preventDefault();
    SpeechRecognition.stopListening();
  };

  const [currentScript, setCurrentScript] = useState();

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div
        style={{
          textAlign: "center",
          position: "sticky",
          top: "0",
          width: "100%",
          backgroundColor: "black",
        }}
      >
        <h1>Voice ChatBot</h1>
      </div>
      <div style={{ width: "500px", marginBottom: "100px" }}>
        <section>
          {chats && chats.length
            ? chats.map((chat, index) => (
                <div
                  key={index}
                  className={`message ${
                    chat.role === "user" ? "user_msg" : "assist_msg"
                  }`}
                >
                  <span>{chat.role === "user" ? <FaUser /> : <FaRobot />}</span>
                  <span>{chat.content}</span>
                  <span>
                    {chat.role === "user" ? (
                      <div />
                    ) : (
                      <button
                        style={{
                          backgroundColor: "none",
                          borderRadius: "20px",
                          paddingBottom: "5px",
                          paddingRight: "8px",
                        }}
                        onClick={() => {
                          if (playing) {
                            if (currentScript === chat.url) {
                              stopSpeech();
                            } else {
                              playTextToSpeech(chat.url);
                              setCurrentScript(chat.url);
                            }
                          } else {
                            playTextToSpeech(chat.url);
                            setCurrentScript(chat.url);
                          }
                        }}
                      >
                        <CiPlay1 />
                      </button>
                    )}
                  </span>
                </div>
              ))
            : ""}
        </section>
      </div>
      <form
        style={{
          position: "fixed",
          width: "510px",
          margin: "auto",
        }}
        onSubmit={(e) => chat(e, message)}
      >
        <div style={{ display: "flex", gap: 3 }}>
          <input
            type="text"
            name="message"
            value={message}
            placeholder="Type a message"
            onChange={(e) => setMessage(e.target.value)}
          />
          <button>
            <AiOutlineSend />
          </button>
          {listening ? (
            <button onClick={handleStop}>
              <SiAudiomack />
            </button>
          ) : (
            <button onClick={handleStart}>
              <AiFillAudio />
            </button>
          )}
        </div>
      </form>
    </main>
  );
}

export default App;
