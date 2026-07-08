import React from "react";
import "./CSS/About.css";

const AboutPage = () => {
  const teamMembers = [
    {
      name: "Rachana Kadlewad",
      role: "Full Stack Developer",
      description:
        "Developed the EchoEats platform by contributing to both frontend and backend development, integrating AI-powered voice recognition, database management, payment gateway integration, and creating a seamless user experience.",
    },
  ];

  return (
    <div className="about-container">
      {/* Header */}
      <div className="about-header">
        <h1>About EchoEats</h1>
        <p>AI Powered Voice-Based Food Ordering System</p>
      </div>

      <div className="about-content">
        {/* Hero Section */}
        <div className="highlight-section">
          <div className="highlight-badge">🚀 INNOVATION</div>

          <h2 className="highlight-title">
            Voice-Based Food Ordering with AI
          </h2>

          <p className="highlight-description">
            EchoEats is an AI-powered food ordering platform that enables users
            to browse menus, place orders, navigate the application, and manage
            their cart using natural voice commands. By combining advanced
            speech recognition with Artificial Intelligence, EchoEats offers a
            fast, smart, and hands-free food ordering experience.
          </p>

          <div className="voice-features">
            <div className="voice-feature">
              <span className="voice-icon">🎤</span>
              <span>Voice-Based Ordering</span>
            </div>

            <div className="voice-feature">
              <span className="voice-icon">🤖</span>
              <span>AI Command Understanding</span>
            </div>

            <div className="voice-feature">
              <span className="voice-icon">⚡</span>
              <span>Instant Voice Recognition</span>
            </div>

            <div className="voice-feature">
              <span className="voice-icon">💳</span>
              <span>Secure Razorpay Payments</span>
            </div>
          </div>
        </div>

        {/* About */}
        <div className="about-section">
          <h2>About EchoEats</h2>

          <p>
            EchoEats is a modern food ordering application that allows users to
            interact with the system using voice commands. Users can browse food
            items, search menus, filter categories, add items to the cart,
            navigate through different pages, and place orders simply by
            speaking.
          </p>

          <p>
            Built using React.js, Django, MySQL, Groq AI, and Web Speech API,
            EchoEats demonstrates how Artificial Intelligence can make everyday
            applications more intuitive, accessible, and user-friendly.
          </p>
        </div>

        {/* Mission */}
        <div className="about-section">
          <h2>Our Mission</h2>

          <p>
            Our mission is to simplify food ordering through Artificial
            Intelligence and voice technology. EchoEats is designed to provide a
            faster, smarter, and more accessible ordering experience for every
            user while showcasing the power of AI in real-world applications.
          </p>
        </div>

        {/* Technology Stack */}
        <div className="about-section">
          <h2>Technology Stack</h2>

          <div className="stats-section">
            <div className="stat-item">
              <h3>React.js</h3>
              <p>Frontend</p>
            </div>

            <div className="stat-item">
              <h3>Django</h3>
              <p>Backend</p>
            </div>

            <div className="stat-item">
              <h3>MySQL</h3>
              <p>Database</p>
            </div>

            <div className="stat-item">
              <h3>Groq AI</h3>
              <p>LLM Integration</p>
            </div>

            <div className="stat-item">
              <h3>Web Speech API</h3>
              <p>Voice Recognition</p>
            </div>

            <div className="stat-item">
              <h3>Razorpay</h3>
              <p>Payment Gateway</p>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="about-section">
          <h2>Key Features</h2>

          <div className="voice-features">
            <div className="voice-feature">
              <span className="voice-icon">🎙️</span>
              <span>Voice-Based Food Ordering</span>
            </div>

            <div className="voice-feature">
              <span className="voice-icon">🍔</span>
              <span>Smart Menu Search</span>
            </div>

            <div className="voice-feature">
              <span className="voice-icon">🛒</span>
              <span>Voice Cart Management</span>
            </div>

            <div className="voice-feature">
              <span className="voice-icon">🧠</span>
              <span>AI Command Processing</span>
            </div>

            <div className="voice-feature">
              <span className="voice-icon">💳</span>
              <span>Secure Online Payments</span>
            </div>

            <div className="voice-feature">
              <span className="voice-icon">📦</span>
              <span>Order History & Tracking</span>
            </div>
          </div>
        </div>

        {/* Team */}
        <div className="team-section">
          <h2>Meet Our Team</h2>

          <div className="team-grid">
            {teamMembers.map((member, index) => (
              <div className="team-card lead" key={index}>
                <div className="team-icon">👩‍💻</div>

                <h3>{member.name}</h3>

                <p className="team-role">{member.role}</p>

                <p className="team-desc">{member.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Project Highlights */}
        <div className="stats-section">
          <div className="stat-item">
            <h3>AI</h3>
            <p>Powered Assistant</p>
          </div>

          <div className="stat-item">
            <h3>Voice</h3>
            <p>Hands-Free Ordering</p>
          </div>

          <div className="stat-item">
            <h3>React + Django</h3>
            <p>Full Stack Project</p>
          </div>

          <div className="stat-item">
            <h3>100%</h3>
            <p>Voice Integrated</p>
          </div>
        </div>

        {/* Footer */}
        <div className="about-section">
          <h2>Why Choose EchoEats?</h2>

          <p
            style={{
              textAlign: "center",
              fontSize: "20px",
              fontWeight: "bold",
            }}
          >
            "Order with Your Voice. Enjoy Every Bite."
          </p>

          <p style={{ textAlign: "center" }}>
            EchoEats showcases how Artificial Intelligence and Voice Recognition
            can transform traditional food ordering into a smarter, faster, and
            more accessible experience for everyone.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;