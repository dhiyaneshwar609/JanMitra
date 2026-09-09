// ======================================================
// JanMitra AI - Main JavaScript
// ======================================================
// Features:
// - Normal text chat
// - Streaming JanMitra responses
// - Local Vosk voice input
// - Multilingual language selector
// - Browser Text-to-Speech
// - Government domain selection
// - Dark/light theme
// - New chat
// ======================================================


// ======================================================
// DOM ELEMENTS
// ======================================================

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat");

const themeBtn = document.getElementById("theme-btn");

const voiceBtn = document.getElementById("voice-btn");
const headerVoiceBtn =
    document.getElementById("header-voice-btn");

const navHome =
    document.getElementById("nav-home");

const navHistory =
    document.getElementById("nav-history");

const navLanguages =
    document.getElementById("nav-languages");

const navSettings =
    document.getElementById("nav-settings");


// ======================================================
// VOICE LANGUAGES
// ======================================================

const VOICE_LANGUAGES = {

    en: {
        name: "English",
        code: "en-IN",
        model: "english"
    },

    ta: {
        name: "தமிழ்",
        code: "ta-IN",
        model: "tamil"
    },

    hi: {
        name: "हिन्दी",
        code: "hi-IN",
        model: "hindi"
    },

    te: {
        name: "తెలుగు",
        code: "te-IN",
        model: "telugu"
    },

    ml: {
        name: "മലയാളം",
        code: "ml-IN",
        model: "malayalam"
    },

    kn: {
        name: "ಕನ್ನಡ",
        code: "kn-IN",
        model: "kannada"
    }

};


// Current selected voice language
let selectedVoiceLanguage = "en";


// ======================================================
// VOICE RECORDING VARIABLES
// ======================================================

let isListening = false;

let mediaStream = null;

let audioContext = null;

let scriptProcessor = null;

let audioSource = null;

let recordedSamples = [];


// ======================================================
// PAGE LOAD
// ======================================================

window.addEventListener("load", function () {

    if (input) {
        input.focus();
    }

    loadTheme();

    updateThemeIcon();

    createLanguageSelector();

});


// ======================================================
// SCROLL TO BOTTOM
// ======================================================

function scrollToBottom() {

    if (!chatBox) {
        return;
    }

    chatBox.scrollTo({

        top: chatBox.scrollHeight,

        behavior: "smooth"

    });

}


// ======================================================
// MARKDOWN FORMATTER
// ======================================================

function formatMarkdown(text) {

    if (!text) {
        return "";
    }

    return text

        .replace(
            /^### (.*)$/gm,
            "<h3>$1</h3>"
        )

        .replace(
            /^## (.*)$/gm,
            "<h2>$1</h2>"
        )

        .replace(
            /^# (.*)$/gm,
            "<h1>$1</h1>"
        )

        .replace(
            /\*\*(.*?)\*\*/g,
            "<b>$1</b>"
        )

        .replace(
            /^- (.*)$/gm,
            "<li>$1</li>"
        )

        .replace(
            /^• (.*)$/gm,
            "<li>$1</li>"
        )

        .replace(
            /(📍|👤|🎁|📄|📝|⚠️|🌐)\s*(.*?):/g,
            "<h3>$1 $2</h3>"
        )

        .replace(
            /\n/g,
            "<br>"
        );

}


// ======================================================
// SOURCE HTML
// ======================================================

function sourceHTML(sources) {

    if (
        !sources ||
        sources.length === 0
    ) {
        return "";
    }

    let html = `
        <div class="sources">

            <h3>
                🌐 Official Sources
            </h3>
    `;

    sources.forEach(function (src) {

        html += `

            <div class="source-card">

                <a
                    href="${src.url}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    ${src.title}
                </a>

                <small>
                    ${src.url}
                </small>

            </div>

        `;

    });

    html += `
        </div>
    `;

    return html;

}


// ======================================================
// CREATE MESSAGE
// ======================================================

function createMessage(
    content,
    sender = "bot",
    sources = null
) {

    if (!chatBox) {
        return;
    }

    const wrapper =
        document.createElement("div");

    wrapper.className =
        sender === "user"
            ? "user-message"
            : "bot-message";


    if (sender === "user") {

        wrapper.innerHTML = `

            <div class="message">
                ${content}
            </div>

        `;

    } else {

        wrapper.innerHTML = `

            <div class="avatar">
                🤖
            </div>

            <div class="message">

                ${formatMarkdown(content)}

                ${sourceHTML(sources)}

            </div>

        `;

    }

    chatBox.appendChild(wrapper);

    scrollToBottom();

}


// ======================================================
// TYPING INDICATOR
// ======================================================

function typingAnimation() {

    if (!chatBox) {
        return;
    }

    const existing =
        document.getElementById("typing");

    if (existing) {
        return;
    }

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "bot-message";

    wrapper.id =
        "typing";

    wrapper.innerHTML = `

        <div class="avatar">
            🤖
        </div>

        <div class="message">

            <div class="typing">

                <span></span>
                <span></span>
                <span></span>

            </div>

        </div>

    `;

    chatBox.appendChild(wrapper);

    scrollToBottom();

}


function removeTyping() {

    const typing =
        document.getElementById("typing");

    if (typing) {
        typing.remove();
    }

}


// ======================================================
// TEXT TO SPEECH
// ======================================================

function speakAnswer(text) {

    if (!text) {
        return;
    }

    if (
        !("speechSynthesis" in window)
    ) {

        console.warn(
            "Text-to-Speech is not supported."
        );

        return;
    }

    window.speechSynthesis.cancel();

    const utterance =
        new SpeechSynthesisUtterance(
            text
        );

    const language =
        VOICE_LANGUAGES[
            selectedVoiceLanguage
        ];

    utterance.lang =
        language
            ? language.code
            : "en-IN";

    utterance.rate = 0.95;

    utterance.pitch = 1;

    utterance.volume = 1;

    window.speechSynthesis.speak(
        utterance
    );

}


// ======================================================
// LANGUAGE SELECTOR
// ======================================================

function createLanguageSelector() {

    if (
        document.getElementById(
            "voice-language-selector"
        )
    ) {
        return;
    }

    const topbarRight =
        document.querySelector(
            ".topbar-right"
        );

    if (!topbarRight) {
        return;
    }

    const wrapper =
        document.createElement("div");

    wrapper.id =
        "voice-language-selector";

    wrapper.style.display =
        "flex";

    wrapper.style.alignItems =
        "center";

    wrapper.style.gap =
        "6px";

    wrapper.style.marginRight =
        "8px";


    wrapper.innerHTML = `

        <span
            style="
                font-size:13px;
                font-weight:500;
            "
            title="Voice Language"
        >
            🌐
        </span>

        <select
            id="voice-language"
            title="Voice Language"
            style="
                padding:6px 8px;
                border-radius:8px;
                border:1px solid #ccc;
                background:inherit;
                font-family:inherit;
                font-size:12px;
                cursor:pointer;
            "
        >

            <option value="en">
                English
            </option>

            <option value="ta">
                தமிழ்
            </option>

            <option value="hi">
                हिन्दी
            </option>

            <option value="te">
                తెలుగు
            </option>

            <option value="ml">
                മലയാളം
            </option>

            <option value="kn">
                ಕನ್ನಡ
            </option>

        </select>

    `;


    topbarRight.insertBefore(
        wrapper,
        headerVoiceBtn
    );


    const selector =
        document.getElementById(
            "voice-language"
        );


    selector.addEventListener(
        "change",
        function () {

            selectedVoiceLanguage =
                this.value;

            const language =
                VOICE_LANGUAGES[
                    selectedVoiceLanguage
                ];


            showToast(
                "Voice language: " +
                language.name
            );

        }
    );

}


// ======================================================
// SEND MESSAGE TO JANMITRA
// ======================================================

async function sendMessage() {

    if (!input || !sendBtn) {
        return;
    }

    const message =
        input.value.trim();


    if (!message) {
        return;
    }


    // Show user question

    createMessage(
        message,
        "user"
    );


    // Clear input

    input.value = "";


    // Disable send

    sendBtn.disabled = true;

    sendBtn.style.opacity = "0.6";


    // Show typing

    typingAnimation();


    try {

        const response =
            await fetch(
                "/chat-stream",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        message: message

                    })

                }
            );


        if (!response.ok) {

            throw new Error(
                "Server returned " +
                response.status
            );

        }


        if (!response.body) {

            throw new Error(
                "No response stream received."
            );

        }


        removeTyping();


        const wrapper =
            document.createElement("div");


        wrapper.className =
            "bot-message";


        wrapper.innerHTML = `

            <div class="avatar">
                🤖
            </div>

            <div class="message"></div>

        `;


        chatBox.appendChild(
            wrapper
        );


        const botMessage =
            wrapper.querySelector(
                ".message"
            );


        const reader =
            response.body.getReader();


        const decoder =
            new TextDecoder();


        let buffer = "";

        let fullAnswer = "";

        let finalSources = [];


        while (true) {

            const {
                done,
                value
            } = await reader.read();


            if (done) {
                break;
            }


            buffer +=
                decoder.decode(
                    value,
                    {
                        stream: true
                    }
                );


            const lines =
                buffer.split("\n");


            buffer =
                lines.pop();


            for (
                const line of lines
            ) {

                if (!line.trim()) {
                    continue;
                }


                try {

                    const msg =
                        JSON.parse(line);


                    if (
                        msg.type ===
                        "chunk"
                    ) {

                        fullAnswer +=
                            msg.data;


                        botMessage.innerHTML =
                            formatMarkdown(
                                fullAnswer
                            );

                    }


                    else if (
                        msg.type ===
                        "done"
                    ) {

                        finalSources =
                            msg.sources || [];


                        botMessage.innerHTML =
                            formatMarkdown(
                                fullAnswer
                            ) +
                            sourceHTML(
                                finalSources
                            );

                    }

                }

                catch (error) {

                    console.warn(
                        "Stream parsing warning:",
                        error
                    );

                }


                chatBox.scrollTop =
                    chatBox.scrollHeight;

            }

        }


        // Speak answer

        if (
            fullAnswer &&
            fullAnswer.trim()
        ) {

            speakAnswer(
                fullAnswer
            );

        }

    }

    catch (error) {

        console.error(
            "Chat error:",
            error
        );


        removeTyping();


        createMessage(
            "❌ Unable to connect to JanMitra AI. Please try again."
        );

    }


    sendBtn.disabled = false;

    sendBtn.style.opacity = "1";

    input.focus();

}


// ======================================================
// SEND BUTTON
// ======================================================

if (sendBtn) {

    sendBtn.addEventListener(
        "click",
        sendMessage
    );

}


// ======================================================
// ENTER KEY
// ======================================================

if (input) {

    input.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );

}


// ======================================================
// GOVERNMENT DOMAINS
// ======================================================

let selectedDomain =
    "general";


const domainPrompts = {

    education:
        "Show education schemes and scholarships for students.",

    health:
        "Show government healthcare schemes and health services.",

    women_child:
        "Show government schemes for women and child welfare.",

    agriculture:
        "Show government schemes and services for farmers and agriculture.",

    employment:
        "Show government employment, jobs and skill development schemes.",

    housing:
        "Show government housing schemes and housing assistance.",

    transport:
        "Show government transport and road-related services and schemes.",

    legal:
        "Show government legal aid schemes and citizen legal services.",

    pension:
        "Show government pension and social security schemes.",

    disability:
        "Show government disability welfare schemes and support services.",

    documents:
        "Show government certificates and citizen document services.",

    general:
        "Show government schemes and citizen services."

};


const domainNames = {

    education:
        "Education",

    health:
        "Health",

    women_child:
        "Women & Child Welfare",

    agriculture:
        "Agriculture",

    employment:
        "Employment",

    housing:
        "Housing",

    transport:
        "Transport",

    legal:
        "Legal Aid",

    pension:
        "Pension & Social Security",

    disability:
        "Disability Welfare",

    documents:
        "Certificates & Documents",

    general:
        "General Government Schemes"

};


// ======================================================
// SELECT DOMAIN
// ======================================================

function selectDomain(domain) {

    selectedDomain =
        domain;


    document
        .querySelectorAll(
            ".sidebar-domain"
        )
        .forEach(
            function (button) {

                button.classList.remove(
                    "active"
                );

            }
        );


    const selectedButton =
        document.querySelector(
            `.sidebar-domain[data-domain="${domain}"]`
        );


    if (selectedButton) {

        selectedButton.classList.add(
            "active"
        );

    }


    if (input) {

        input.placeholder =
            "Ask about " +
            (
                domainNames[domain] ||
                domainNames.general
            ) +
            "...";

    }


    if (input) {

        input.value =
            domainPrompts[domain] ||
            domainPrompts.general;

    }


    sendMessage();

}


// ======================================================
// QUICK PROMPT
// ======================================================

function quickPrompt(text) {

    if (!input) {
        return;
    }

    input.value =
        text;

    sendMessage();

}


// ======================================================
// NEW CHAT
// ======================================================

if (newChatBtn) {

    newChatBtn.addEventListener(
        "click",
        function () {

            chatBox.innerHTML = `

                <div class="welcome-card">

                    <div class="welcome-icon">
                        🤖
                    </div>

                    <h2>
                        Welcome to JanMitra AI
                    </h2>

                    <p>
                        Your AI-powered citizen assistant
                        for Government Schemes, Education,
                        Healthcare, Agriculture, Employment
                        and Public Services.
                    </p>

                    <div class="welcome-hint">

                        <i
                            class="fa-solid fa-arrow-left">
                        </i>

                        <span>
                            Select a government domain
                            from the left panel to get started.
                        </span>

                    </div>

                </div>

                <div
                    id="messages-container"
                    class="messages-container">
                </div>

            `;


            selectedDomain =
                "general";


            document
                .querySelectorAll(
                    ".sidebar-domain"
                )
                .forEach(
                    function (button) {

                        button.classList.remove(
                            "active"
                        );

                    }
                );


            input.placeholder =
                "Ask about government schemes, certificates, scholarships...";


            input.value = "";


            // Stop speech

            if (
                "speechSynthesis" in window
            ) {

                window.speechSynthesis.cancel();

            }


            input.focus();

        }
    );

}


// ======================================================
// TOAST
// ======================================================

function showToast(
    message,
    isError = false
) {

    const toast =
        document.getElementById(
            "toast"
        );

    const toastText =
        document.getElementById(
            "toast-text"
        );


    if (
        !toast ||
        !toastText
    ) {

        console.log(message);

        return;

    }


    toastText.textContent =
        message;


    toast.style.background =
        isError
            ? "#dc2626"
            : "#16a34a";


    toast.classList.add(
        "show"
    );


    setTimeout(
        function () {

            toast.classList.remove(
                "show"
            );

        },
        2500
    );

}


// ======================================================
// THEME
// ======================================================

function updateThemeIcon() {

    if (!themeBtn) {
        return;
    }


    const icon =
        themeBtn.querySelector("i");


    if (!icon) {
        return;
    }


    const isDark =
        document.body.classList.contains(
            "dark"
        );


    if (isDark) {

        icon.className =
            "fa-solid fa-sun";


        themeBtn.title =
            "Switch to light mode";

    }

    else {

        icon.className =
            "fa-solid fa-moon";


        themeBtn.title =
            "Switch to dark mode";

    }

}


function loadTheme() {

    const savedTheme =
        localStorage.getItem(
            "janmitra-theme"
        );


    document.body.classList.remove(
        "dark",
        "dark-mode"
    );


    if (
        savedTheme ===
        "dark"
    ) {

        document.body.classList.add(
            "dark",
            "dark-mode"
        );

    }


    updateThemeIcon();

}


// ======================================================
// THEME TOGGLE
// ======================================================

function applyTheme(theme) {

    if (theme === "dark") {

        document.body.classList.add("dark");

        document.body.classList.remove("light");

        localStorage.setItem(
            "janmitra-theme",
            "dark"
        );

    } else {

        document.body.classList.remove("dark");

        document.body.classList.add("light");

        localStorage.setItem(
            "janmitra-theme",
            "light"
        );

    }

    updateThemeIcon();

}


// ------------------------------------------------------
// Theme button
// ------------------------------------------------------

function toggleTheme() {

    const isDark =
        document.body.classList.contains("dark");

    if (isDark) {

        applyTheme("light");

    } else {

        applyTheme("dark");

    }

}


// ------------------------------------------------------
// Load saved theme
// ------------------------------------------------------

function loadTheme() {

    const savedTheme =
        localStorage.getItem("janmitra-theme");

    if (savedTheme === "dark") {

        applyTheme("dark");

    } else {

        applyTheme("light");

    }

}


// ------------------------------------------------------
// Attach theme button
// ------------------------------------------------------

if (themeBtn) {

    themeBtn.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            event.stopPropagation();

            toggleTheme();

        }
    );

}


// ------------------------------------------------------
// Settings modal theme button
// ------------------------------------------------------

const modalThemeButton =
    document.getElementById("theme-toggle-modal");

if (modalThemeButton) {

    modalThemeButton.addEventListener(
        "click",
        function (event) {

            event.preventDefault();
            event.stopPropagation();

            toggleTheme();

        }
    );

}




// ======================================================
// LOCAL VOSK VOICE INPUT
// ======================================================


// ------------------------------------------------------
// Microphone state
// ------------------------------------------------------

function setMicState(
    listening
) {

    isListening =
        listening;


    const buttons = [

        voiceBtn,

        headerVoiceBtn

    ];


    buttons.forEach(
        function (button) {

            if (!button) {
                return;
            }


            const icon =
                button.querySelector(
                    "i"
                );


            if (!icon) {
                return;
            }


            if (listening) {

                button.classList.add(
                    "listening"
                );


                icon.className =
                    "fa-solid fa-stop";


                button.title =
                    "Stop voice input";

            }

            else {

                button.classList.remove(
                    "listening"
                );


                icon.className =
                    "fa-solid fa-microphone";


                button.title =
                    "Voice Input";

            }

        }
    );

}


// ------------------------------------------------------
// Float32 audio → WAV
// ------------------------------------------------------

function encodeWAV(
    samples,
    sampleRate
) {

    const buffer =
        new ArrayBuffer(
            44 +
            samples.length * 2
        );


    const view =
        new DataView(
            buffer
        );


    function writeString(
        offset,
        string
    ) {

        for (
            let i = 0;
            i < string.length;
            i++
        ) {

            view.setUint8(
                offset + i,
                string.charCodeAt(i)
            );

        }

    }


    writeString(
        0,
        "RIFF"
    );


    view.setUint32(
        4,
        36 +
        samples.length * 2,
        true
    );


    writeString(
        8,
        "WAVE"
    );


    writeString(
        12,
        "fmt "
    );


    view.setUint32(
        16,
        16,
        true
    );


    // PCM

    view.setUint16(
        20,
        1,
        true
    );


    // Mono

    view.setUint16(
        22,
        1,
        true
    );


    view.setUint32(
        24,
        sampleRate,
        true
    );


    view.setUint32(
        28,
        sampleRate * 2,
        true
    );


    view.setUint16(
        32,
        2,
        true
    );


    // 16 bit

    view.setUint16(
        34,
        16,
        true
    );


    writeString(
        36,
        "data"
    );


    view.setUint32(
        40,
        samples.length * 2,
        true
    );


    let offset = 44;


    for (
        let i = 0;
        i < samples.length;
        i++
    ) {

        let sample =
            Math.max(
                -1,
                Math.min(
                    1,
                    samples[i]
                )
            );


        sample =
            sample < 0
                ? sample * 0x8000
                : sample * 0x7FFF;


        view.setInt16(
            offset,
            sample,
            true
        );


        offset += 2;

    }


    return new Blob(
        [view],
        {
            type: "audio/wav"
        }
    );

}


// ------------------------------------------------------
// Resample microphone audio to 16 kHz
// ------------------------------------------------------

function resampleTo16k(
    samples,
    originalSampleRate
) {

    const targetSampleRate =
        16000;


    if (
        originalSampleRate ===
        targetSampleRate
    ) {

        return samples;

    }


    const ratio =
        originalSampleRate /
        targetSampleRate;


    const newLength =
        Math.round(
            samples.length /
            ratio
        );


    const result =
        new Float32Array(
            newLength
        );


    for (
        let i = 0;
        i < newLength;
        i++
    ) {

        const position =
            i * ratio;


        const left =
            Math.floor(
                position
            );


        const right =
            Math.min(
                left + 1,
                samples.length - 1
            );


        const fraction =
            position - left;


        result[i] =
            samples[left] *
                (1 - fraction) +
            samples[right] *
                fraction;

    }


    return result;

}


// ------------------------------------------------------
// Send recorded audio to Flask/Vosk
// ------------------------------------------------------

async function sendAudioToVosk() {

    if (
        recordedSamples.length === 0
    ) {

        showToast(
            "No voice was recorded.",
            true
        );

        return;

    }


    showToast(
        "🧠 Processing your voice..."
    );


    try {

        const combinedLength =
            recordedSamples.reduce(
                function (
                    total,
                    chunk
                ) {

                    return (
                        total +
                        chunk.length
                    );

                },
                0
            );


        const combined =
            new Float32Array(
                combinedLength
            );


        let offset = 0;


        recordedSamples.forEach(
            function (chunk) {

                combined.set(
                    chunk,
                    offset
                );


                offset +=
                    chunk.length;

            }
        );


        const originalRate =
            audioContext
                ? audioContext.sampleRate
                : 48000;


        const samples16k =
            resampleTo16k(
                combined,
                originalRate
            );


        const wavBlob =
            encodeWAV(
                samples16k,
                16000
            );


        const formData =
            new FormData();


        formData.append(
            "audio",
            wavBlob,
            "voice.wav"
        );


        formData.append(
            "language",
            selectedVoiceLanguage
        );


        const response =
            await fetch(
                "/voice-to-text",
                {
                    method: "POST",
                    body: formData
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.error ||
                "Voice server error."
            );

        }


        if (!result.success) {

            throw new Error(
                result.error ||
                "Voice recognition failed."
            );

        }


        const transcript =
            (
                result.text ||
                ""
            ).trim();


        if (!transcript) {

            showToast(
                "I could not understand the speech. Please try again.",
                true
            );

            return;

        }


        // Put recognized text into input

        input.value =
            transcript;


        input.focus();


        showToast(
            "✅ Voice captured"
        );


        // Automatically send to JanMitra

        setTimeout(
            function () {

                sendMessage();

            },
            300
        );

    }

    catch (error) {

        console.error(
            "Vosk voice error:",
            error
        );


        showToast(
            "❌ Voice recognition failed: " +
            error.message,
            true
        );

    }

}


// ------------------------------------------------------
// Start microphone
// ------------------------------------------------------

async function startVoiceRecognition() {

    if (isListening) {

        await stopVoiceRecording();

        return;

    }


    try {

        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia
        ) {

            throw new Error(
                "Browser microphone access is unavailable."
            );

        }


        mediaStream =
            await navigator.mediaDevices
                .getUserMedia({

                    audio: {

                        channelCount: 1,

                        echoCancellation:
                            true,

                        noiseSuppression:
                            true,

                        autoGainControl:
                            true

                    }

                });


        const AudioContext =
            window.AudioContext ||
            window.webkitAudioContext;


        if (!AudioContext) {

            throw new Error(
                "Web Audio API is not supported."
            );

        }


        audioContext =
            new AudioContext();


        audioSource =
            audioContext
                .createMediaStreamSource(
                    mediaStream
                );


        scriptProcessor =
            audioContext
                .createScriptProcessor(
                    4096,
                    1,
                    1
                );


        recordedSamples = [];


        scriptProcessor.onaudioprocess =
            function (event) {

                if (!isListening) {
                    return;
                }


                const inputData =
                    event.inputBuffer
                        .getChannelData(0);


                recordedSamples.push(
                    new Float32Array(
                        inputData
                    )
                );

            };


        audioSource.connect(
            scriptProcessor
        );


        scriptProcessor.connect(
            audioContext.destination
        );


        setMicState(
            true
        );


        showToast(
            "🎤 Listening... Click the microphone again when you finish."
        );

    }

    catch (error) {

        console.error(
            "Microphone error:",
            error
        );


        setMicState(
            false
        );


        if (
            error.name ===
            "NotAllowedError"
        ) {

            showToast(
                "Microphone permission was denied. Please allow microphone access.",
                true
            );

        }

        else if (
            error.name ===
            "NotFoundError"
        ) {

            showToast(
                "No microphone was found.",
                true
            );

        }

        else {

            showToast(
                "Could not access the microphone: " +
                error.message,
                true
            );

        }

    }

}


// ------------------------------------------------------
// Stop microphone
// ------------------------------------------------------

async function stopVoiceRecording() {

    if (!isListening) {
        return;
    }


    setMicState(
        false
    );


    if (scriptProcessor) {

        scriptProcessor.disconnect();

        scriptProcessor.onaudioprocess =
            null;

        scriptProcessor = null;

    }


    if (audioSource) {

        try {

            audioSource.disconnect();

        }

        catch (error) {

            console.warn(
                "Audio source disconnect warning:",
                error
            );

        }

        audioSource = null;

    }


    if (mediaStream) {

        mediaStream
            .getTracks()
            .forEach(
                function (track) {

                    track.stop();

                }
            );


        mediaStream = null;

    }


    if (audioContext) {

        try {

            await audioContext.close();

        }

        catch (error) {

            console.warn(
                "Audio context close warning:",
                error
            );

        }


        audioContext = null;

    }


    showToast(
        "⏹ Recording stopped"
    );


    await sendAudioToVosk();

}


// ======================================================
// MICROPHONE BUTTONS
// ======================================================

if (voiceBtn) {

    voiceBtn.addEventListener(
        "click",
        startVoiceRecognition
    );

}


if (headerVoiceBtn) {

    headerVoiceBtn.addEventListener(
        "click",
        startVoiceRecognition
    );

}


// ======================================================
// SIDEBAR NAVIGATION
// ======================================================

if (navHome) {

    navHome.addEventListener(
        "click",
        function () {

            document
                .querySelectorAll(
                    ".sidebar-nav a"
                )
                .forEach(
                    function (item) {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


            navHome.classList.add(
                "active"
            );


            chatBox.scrollTo({

                top: 0,

                behavior: "smooth"

            });

        }
    );

}


if (navHistory) {

    navHistory.addEventListener(
        "click",
        function () {

            showToast(
                "Chat history will be added in the next version."
            );

        }
    );

}


if (navLanguages) {

    navLanguages.addEventListener(
        "click",
        function () {

            showToast(
                "Use the 🌐 voice language selector to choose your voice language."
            );

        }
    );

}


if (navSettings) {

    navSettings.addEventListener(
        "click",
        function () {

            showToast(
                "Settings will be added in the next version."
            );

        }
    );

}


// ======================================================
// END
// ======================================================