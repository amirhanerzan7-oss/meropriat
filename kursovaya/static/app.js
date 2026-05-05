// UX: меню, анимации, сервис-модалка, эффекты.
(function () {
  "use strict";

  var menuBtn = document.getElementById("menu-btn");
  var nav = document.getElementById("main-nav");

  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      nav.classList.toggle("show");
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("show");
      });
    });
  }

  // Карточки сервисов: показываем модальное описание, чтобы кнопки работали.
  var modal = document.getElementById("service-modal");
  var modalTitle = document.getElementById("service-modal-title");
  var modalText = document.getElementById("service-modal-text");
  var modalClose = document.getElementById("service-modal-close");
  var serviceButtons = document.querySelectorAll(".service-btn");

  var serviceContent = {
    crm: {
      title: "CRM",
      text: "Сегментация участников, заметки, статусы оплаты и история взаимодействий в одном окне."
    },
    checkin: {
      title: "Check-in",
      text: "Быстрый вход по списку, QR/телефону, и моментальная отметка присутствия гостей."
    },
    reminders: {
      title: "Auto Reminders",
      text: "Автоматические напоминания за 24 часа и за 1 час до старта мероприятия."
    },
    analytics: {
      title: "Analytics",
      text: "Конверсия, динамика регистраций, популярные события и отчеты для организатора."
    }
  };

  function openServiceModal(key) {
    if (!modal || !modalTitle || !modalText) return;
    var item = serviceContent[key] || { title: "Service", text: "Information coming soon." };
    modalTitle.textContent = item.title;
    modalText.textContent = item.text;
    modal.classList.remove("hidden");
    modal.classList.add("show");
    modal.setAttribute("aria-hidden", "false");
  }

  function closeServiceModal() {
    if (!modal) return;
    modal.classList.remove("show");
    modal.setAttribute("aria-hidden", "true");
    setTimeout(function () {
      modal.classList.add("hidden");
    }, 220);
  }

  serviceButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      openServiceModal(btn.getAttribute("data-service"));
    });
  });
  if (modalClose) modalClose.addEventListener("click", closeServiceModal);
  if (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeServiceModal();
    });
  }

  // Плавное появление секций при прокрутке.
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.16 }
    );
    revealEls.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add("visible");
    });
  }

  // Анимируем числовые счетчики в hero.
  document.querySelectorAll(".hero-stats span").forEach(function (node) {
    var target = parseInt(node.textContent || "0", 10);
    if (Number.isNaN(target)) return;
    var start = 0;
    var step = Math.max(1, Math.ceil(target / 26));
    var timer = setInterval(function () {
      start += step;
      if (start >= target) {
        node.textContent = String(target);
        clearInterval(timer);
        return;
      }
      node.textContent = String(start);
    }, 30);
  });

  // Легкий параллакс в hero для "живого" ощущения.
  var hero = document.querySelector(".hero");
  if (hero) {
    window.addEventListener("mousemove", function (e) {
      var x = (e.clientX / window.innerWidth - 0.5) * 8;
      var y = (e.clientY / window.innerHeight - 0.5) * 8;
      hero.style.backgroundPosition = x + "px " + y + "px";
    });
  }

  setTimeout(function () {
    document.querySelectorAll(".flash").forEach(function (flash) {
      flash.style.transition = "opacity .35s ease";
      flash.style.opacity = "0";
      setTimeout(function () {
        flash.remove();
      }, 350);
    });
  }, 3500);
})();
