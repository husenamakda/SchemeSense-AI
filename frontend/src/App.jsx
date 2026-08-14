import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";


function App() {

  const [text, setText] = useState("");

  const [profile, setProfile] = useState(null);

  const [schemes, setSchemes] = useState([]);

  const [comparison, setComparison] = useState([]);

  const [bestScheme, setBestScheme] = useState(null);

  const [recommendation, setRecommendation] = useState("");

  const [loading, setLoading] = useState(false);

  const [aiLoading, setAiLoading] = useState(false);

  const [chatQuestion, setChatQuestion] = useState("");

  const [chatMessages, setChatMessages] = useState([]);

  const [chatLoading, setChatLoading] = useState(false);


  // ==========================================================
  // FIND SCHEMES
  // ==========================================================

  const findSchemes = async () => {

    if (!text.trim()) {

      alert(
        "Please enter your details."
      );

      return;
    }

    setLoading(true);

    setAiLoading(false);

    setProfile(null);

    setSchemes([]);

    setComparison([]);

    setBestScheme(null);

    setRecommendation("");

    setChatMessages([]);


    try {

      // ------------------------------------------------------
      // STEP 1
      // FAST PROFILE + ELIGIBILITY
      // ------------------------------------------------------

      const analysisResponse =
        await axios.post(
          "http://127.0.0.1:8000/analyze",
          {
            text: text
          }
        );


      const data =
        analysisResponse.data;


      setProfile(
        data.profile
      );

      setSchemes(
        data.eligible_schemes || []
      );

      setComparison(
        data.comparison || []
      );

      setBestScheme(
        data.best_scheme || null
      );


      // ------------------------------------------------------
      // STEP 2
      // STOP MAIN LOADING
      // ------------------------------------------------------

      setLoading(false);


      // ------------------------------------------------------
      // STEP 3
      // AI GENERATION
      // ------------------------------------------------------

      setAiLoading(true);


      const recommendationResponse =
        await axios.post(
          "http://127.0.0.1:8000/recommend",
          {
            text: text,
            profile: data.profile,
            eligible_schemes:
              data.eligible_schemes || [],
            best_scheme:
              data.best_scheme || null
          }
        );


      setRecommendation(
        recommendationResponse.data.answer
      );

    } catch (error) {

      console.error(error);

      setLoading(false);

      setAiLoading(false);


      if (error.response) {

        alert(
          `Status: ${error.response.status}\n\n` +
          JSON.stringify(
            error.response.data,
            null,
            2
          )
        );

      } else {

        alert(
          "Unable to connect to SchemeSense AI backend."
        );
      }

    } finally {

      setLoading(false);

      setAiLoading(false);
    }
  };


  // ==========================================================
  // FOLLOW-UP CHAT
  // ==========================================================

  const sendChat = async () => {

    if (!chatQuestion.trim()) {
      return;
    }

    const question =
      chatQuestion.trim();


    setChatQuestion("");


    setChatMessages(
      previous => [
        ...previous,
        {
          role: "user",
          text: question
        }
      ]
    );


    setChatLoading(true);


    try {

      const response =
        await axios.post(
          "http://127.0.0.1:8000/chat",
          {
            question: question,
            profile: profile,
            eligible_schemes: schemes
          }
        );


      setChatMessages(
        previous => [
          ...previous,
          {
            role: "assistant",
            text:
              response.data.answer
          }
        ]
      );

    } catch (error) {

      console.error(error);

      setChatMessages(
        previous => [
          ...previous,
          {
            role: "assistant",
            text:
              "Sorry, I could not process that question."
          }
        ]
      );

    } finally {

      setChatLoading(false);
    }
  };


  // ==========================================================
  // CHAT ENTER KEY
  // ==========================================================

  const handleChatKeyDown = (
    event
  ) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendChat();
    }
  };


  return (

    <div className="min-h-screen bg-slate-100 py-10">

      <div className="max-w-6xl mx-auto px-6">


        {/* ================================================== */}
        {/* HEADER */}
        {/* ================================================== */}

        <div className="text-center mb-10">

          <h1 className="text-5xl font-bold">
            🤖 SchemeSense AI
          </h1>

          <p className="text-gray-600 mt-3 text-lg">
            AI Powered Government Scheme Recommendation System
          </p>

          <p className="text-gray-500 mt-2">
            Personalized • Intelligent • Multilingual
          </p>

        </div>


        {/* ================================================== */}
        {/* INPUT */}
        {/* ================================================== */}

        <div className="bg-white rounded-2xl shadow-xl p-8">

          <h2 className="text-2xl font-bold mb-4">
            Tell us about yourself
          </h2>


          <textarea
            rows={6}
            className="w-full border border-gray-300 rounded-xl p-4 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={
              "Example:\n\n" +
              "I am a 20 year old engineering student " +
              "from Karnataka. My family income is 300000.\n\n" +
              "You can also write in Hindi, Kannada, Gujarati, " +
              "Tamil or English."
            }
            value={text}
            onChange={(e) =>
              setText(e.target.value)
            }
          />


          <button
            onClick={findSchemes}
            disabled={loading}
            className="mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-8 py-3 rounded-xl text-lg font-semibold"
          >

            {loading
              ? "Analyzing Profile..."
              : "Find My Schemes"
            }

          </button>

        </div>


        {/* ================================================== */}
        {/* PROFILE */}
        {/* ================================================== */}

        {profile && (

          <div className="bg-white rounded-2xl shadow-xl mt-8 p-8">

            <h2 className="text-2xl font-bold mb-6">
              👤 Your Profile
            </h2>


            <div className="grid md:grid-cols-2 gap-6">

              <div>
                <p className="font-semibold">
                  Age
                </p>

                <p>
                  {profile.age ?? "-"}
                </p>
              </div>


              <div>
                <p className="font-semibold">
                  State
                </p>

                <p>
                  {profile.state ?? "-"}
                </p>
              </div>


              <div>
                <p className="font-semibold">
                  Occupation
                </p>

                <p>
                  {profile.occupation ?? "-"}
                </p>
              </div>


              <div>
                <p className="font-semibold">
                  Education
                </p>

                <p>
                  {profile.education ?? "-"}
                </p>
              </div>


              <div>
                <p className="font-semibold">
                  Annual Income
                </p>

                <p>
                  {profile.income
                    ? `₹${Number(
                        profile.income
                      ).toLocaleString("en-IN")}`
                    : "-"
                  }
                </p>
              </div>

            </div>

          </div>
        )}


        {/* ================================================== */}
        {/* ELIGIBLE SCHEMES */}
        {/* ================================================== */}

        {schemes.length > 0 && (

          <div className="mt-10">

            <h2 className="text-3xl font-bold mb-6">
              🎓 Eligible Schemes
            </h2>


            <p className="text-gray-600 mb-6">
              We found{" "}
              <span className="font-bold">
                {schemes.length}
              </span>{" "}
              eligible scheme
              {schemes.length !== 1
                ? "s"
                : ""
              }.
            </p>


            {schemes.map(
              scheme => (

                <div
                  key={scheme.id}
                  className="bg-white rounded-2xl shadow-lg p-7 mb-6 border-l-4 border-blue-500"
                >

                  <div className="flex justify-between items-start gap-4">

                    <h3 className="text-2xl font-bold">
                      {scheme.name}
                    </h3>


                    {bestScheme &&
                      bestScheme.id === scheme.id && (

                        <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-semibold whitespace-nowrap">
                          ⭐ Best Option
                        </span>

                    )}

                  </div>


                  <p className="text-green-600 font-bold text-lg mt-3">
                    {scheme.benefit}
                  </p>


                  <h4 className="font-semibold mt-5">
                    Why you're eligible:
                  </h4>


                  <ul className="list-disc ml-6 mt-2 space-y-1">

                    {scheme.why_eligible?.map(
                      (reason, index) => (

                        <li key={index}>
                          {reason}
                        </li>

                      )
                    )}

                  </ul>


                  {(
                    scheme.application_url ||
                    scheme.apply_url
                  ) && (

                    <a
                      href={
                        scheme.application_url ||
                        scheme.apply_url
                      }
                      target="_blank"
                      rel="noreferrer"
                      className="inline-block mt-6 bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg font-semibold"
                    >
                      🔗 Apply Now
                    </a>

                  )}

                </div>

              )
            )}

          </div>
        )}


        {/* ================================================== */}
        {/* COMPARISON */}
        {/* ================================================== */}

        {comparison.length > 0 && (

          <div className="bg-white rounded-2xl shadow-xl mt-10 p-8">

            <h2 className="text-3xl font-bold mb-6">
              📊 Scheme Comparison
            </h2>


            <div className="overflow-x-auto">

              <table className="w-full border-collapse">

                <thead>

                  <tr className="bg-slate-100">

                    <th className="border p-4 text-left">
                      Scheme
                    </th>

                    <th className="border p-4 text-left">
                      Benefit
                    </th>

                    <th className="border p-4 text-left">
                      Maximum Income
                    </th>

                    <th className="border p-4 text-left">
                      Education
                    </th>

                    <th className="border p-4 text-left">
                      State
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {comparison.map(
                    scheme => (

                      <tr
                        key={scheme.id}
                        className="hover:bg-slate-50"
                      >

                        <td className="border p-4 font-semibold">
                          {scheme.name}
                        </td>

                        <td className="border p-4 text-green-600 font-semibold">
                          {scheme.benefit}
                        </td>

                        <td className="border p-4">
                          ₹{Number(
                            scheme.max_income || 0
                          ).toLocaleString(
                            "en-IN"
                          )}
                        </td>

                        <td className="border p-4">
                          {scheme.education}
                        </td>

                        <td className="border p-4">
                          {Array.isArray(
                            scheme.states
                          )
                            ? scheme.states.join(
                                ", "
                              )
                            : scheme.states
                          }
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          </div>
        )}


        {/* ================================================== */}
        {/* BEST OPTION */}
        {/* ================================================== */}

        {bestScheme && (

          <div className="bg-yellow-50 border border-yellow-300 rounded-2xl shadow-lg mt-8 p-7">

            <h2 className="text-2xl font-bold mb-3">
              🏆 Best Option
            </h2>


            <h3 className="text-xl font-bold">
              {bestScheme.name}
            </h3>


            <p className="text-green-700 font-semibold mt-2">
              {bestScheme.benefit}
            </p>


            <p className="text-gray-700 mt-3">
              This option has the highest explicitly stated
              monetary benefit among the eligible schemes
              in the available database.
            </p>

          </div>

        )}


        {/* ================================================== */}
        {/* AI RECOMMENDATION */}
        {/* ================================================== */}

        {(recommendation || aiLoading) && (

          <div className="bg-blue-50 border border-blue-200 rounded-2xl shadow-xl mt-8 p-8">

            <h2 className="text-3xl font-bold mb-6">
              🤖 AI Recommendation
            </h2>


            {aiLoading && !recommendation && (

              <div className="flex items-center gap-3 text-gray-600">

                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>

                <span>
                  Phi-3 is generating your personalized recommendation...
                </span>

              </div>

            )}


            {recommendation && (

              <div className="prose prose-lg max-w-none">

                <ReactMarkdown>
                  {recommendation}
                </ReactMarkdown>

              </div>

            )}

          </div>

        )}


        {/* ================================================== */}
        {/* CHAT */}
        {/* ================================================== */}

        {profile && schemes.length > 0 && (

          <div className="bg-white rounded-2xl shadow-xl mt-10 p-8 mb-10">

            <h2 className="text-3xl font-bold mb-2">
              💬 Ask SchemeSense AI
            </h2>


            <p className="text-gray-600 mb-6">
              Ask follow-up questions about your eligible schemes.
            </p>


            {chatMessages.length > 0 && (

              <div className="space-y-4 mb-6">

                {chatMessages.map(
                  (message, index) => (

                    <div
                      key={index}
                      className={
                        message.role === "user"
                          ? "bg-blue-100 rounded-xl p-4 ml-12"
                          : "bg-slate-100 rounded-xl p-4 mr-12"
                      }
                    >

                      <p className="font-semibold mb-2">

                        {message.role === "user"
                          ? "You"
                          : "🤖 SchemeSense AI"
                        }

                      </p>


                      <div className="prose max-w-none">

                        <ReactMarkdown>
                          {message.text}
                        </ReactMarkdown>

                      </div>

                    </div>

                  )
                )}

              </div>

            )}


            <div className="flex gap-3">

              <textarea
                rows={2}
                className="flex-1 border border-gray-300 rounded-xl p-4 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={
                  "Ask something...\n" +
                  "Example: Which scheme gives the highest scholarship?"
                }
                value={chatQuestion}
                onChange={(e) =>
                  setChatQuestion(
                    e.target.value
                  )
                }
                onKeyDown={
                  handleChatKeyDown
                }
              />


              <button
                onClick={sendChat}
                disabled={
                  chatLoading ||
                  !chatQuestion.trim()
                }
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 rounded-xl font-semibold"
              >

                {chatLoading
                  ? "..."
                  : "Send"
                }

              </button>

            </div>


            <div className="flex flex-wrap gap-2 mt-4">

              <button
                onClick={() =>
                  setChatQuestion(
                    "Which scheme has the highest benefit?"
                  )
                }
                className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-full text-sm"
              >
                💰 Highest benefit?
              </button>


              <button
                onClick={() =>
                  setChatQuestion(
                    "Why am I eligible for these schemes?"
                  )
                }
                className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-full text-sm"
              >
                🎯 Why am I eligible?
              </button>


              <button
                onClick={() =>
                  setChatQuestion(
                    "Compare my eligible schemes."
                  )
                }
                className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-full text-sm"
              >
                📊 Compare schemes
              </button>


              <button
                onClick={() =>
                  setChatQuestion(
                    "Which scheme should I prioritize?"
                  )
                }
                className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-full text-sm"
              >
                🏆 Which should I choose?
              </button>

            </div>

          </div>

        )}

      </div>

    </div>
  );
}


export default App;