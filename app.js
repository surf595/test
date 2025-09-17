const consultationForm = document.getElementById('consultation-form');
const consultationList = document.getElementById('consultation-list');
const seatCountInput = document.getElementById('seat-count');
const applySeatCountButton = document.getElementById('apply-seat-count');
const addSeatButton = document.getElementById('add-seat');
const participantNameInput = document.getElementById('participant-name');
const startSeatSelectionButton = document.getElementById('start-seat-selection');
const selectionMessage = document.getElementById('selection-message');
const circle = document.getElementById('circle');
const participantList = document.getElementById('participant-list');

let consultations = [];
let seats = [];
let currentParticipant = null;
let seatIdCounter = 0;

function generateId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `consultation-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function formatDateTime(value) {
  if (!value) return '';
  const date = new Date(value);
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

function renderConsultations() {
  consultationList.innerHTML = '';
  if (!consultations.length) {
    const empty = document.createElement('li');
    empty.className = 'consultation-list__empty';
    empty.textContent = 'Пока нет запланированных консультаций';
    consultationList.appendChild(empty);
    return;
  }

  consultations
    .slice()
    .sort((a, b) => new Date(a.datetime) - new Date(b.datetime))
    .forEach((item) => {
      const li = document.createElement('li');
      li.className = 'consultation-item';

      const header = document.createElement('div');
      header.className = 'consultation-item__header';

      const client = document.createElement('span');
      client.textContent = item.client;
      const date = document.createElement('span');
      date.textContent = formatDateTime(item.datetime);
      header.appendChild(client);
      header.appendChild(date);

      const meta = document.createElement('div');
      meta.className = 'consultation-item__meta';
      const durationText = item.duration ? `${item.duration} мин` : 'длительность не указана';
      meta.appendChild(document.createTextNode(`${durationText} · `));
      if (item.link) {
        const linkElement = document.createElement('a');
        linkElement.href = item.link;
        linkElement.target = '_blank';
        linkElement.rel = 'noopener';
        linkElement.textContent = 'Перейти на встречу';
        meta.appendChild(linkElement);
      } else {
        meta.appendChild(document.createTextNode('Ссылка появится позже'));
      }

      const notes = document.createElement('p');
      notes.textContent = item.notes || 'Без дополнительных заметок';

      li.appendChild(header);
      li.appendChild(meta);
      li.appendChild(notes);
      consultationList.appendChild(li);
    });
}

if (consultationForm) {
  consultationForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(consultationForm);

    const entry = {
      id: generateId(),
      client: String(data.get('client') || '').trim(),
      datetime: data.get('datetime'),
      duration: Number(data.get('duration')) || null,
    };

    const link = data.get('link');
    entry.link = link ? String(link).trim() : '';

    const notes = data.get('notes');
    entry.notes = notes ? String(notes).trim() : '';

    if (!entry.client || !entry.datetime) {
      return;
    }

    consultations.push(entry);
    renderConsultations();
    consultationForm.reset();
  });
}

function initializeSeats(count) {
  seats = Array.from({ length: count }, () => ({ id: seatIdCounter++, occupant: null }));
  renderSeats();
  renderParticipantList();
}

function resizeSeats(count) {
  const activeParticipants = seats.filter((seat) => seat.occupant).map((seat) => seat.occupant);
  if (count < activeParticipants.length) {
    showSelectionMessage(
      `Невозможно уменьшить круг: уже занято мест — ${activeParticipants.length}.`,
      'error',
    );
    seatCountInput.value = seats.length;
    return;
  }

  const newSeats = [];
  for (let i = 0; i < count; i += 1) {
    if (seats[i]) {
      newSeats.push(seats[i]);
    } else {
      newSeats.push({ id: seatIdCounter++, occupant: null });
    }
  }

  seats = newSeats;
  renderSeats();
  renderParticipantList();
}

function addSeat() {
  seats.push({ id: seatIdCounter++, occupant: null });
  seatCountInput.value = seats.length;
  showSelectionMessage('Добавлено одно свободное место в круге.', 'success');
  renderSeats();
  renderParticipantList();
}

function showSelectionMessage(text, tone = 'neutral') {
  selectionMessage.textContent = text;
  selectionMessage.classList.remove('selection-message--success', 'selection-message--error');
  if (tone === 'success') {
    selectionMessage.classList.add('selection-message--success');
  }
  if (tone === 'error') {
    selectionMessage.classList.add('selection-message--error');
  }
}

function renderSeats() {
  circle.innerHTML = '';
  const bounds = circle.getBoundingClientRect();
  const size = bounds.width || circle.offsetWidth;
  if (!size) {
    window.requestAnimationFrame(renderSeats);
    return;
  }
  const radius = size / 2 - 45;
  const centerX = size / 2;
  const centerY = size / 2;

  seats.forEach((seat, index) => {
    const angle = (2 * Math.PI * index) / seats.length - Math.PI / 2;
    const x = centerX + radius * Math.cos(angle) - 36;
    const y = centerY + radius * Math.sin(angle) - 36;

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'seat';
    button.style.left = `${x}px`;
    button.style.top = `${y}px`;
    button.dataset.id = seat.id;

    const seatIndex = document.createElement('span');
    seatIndex.className = 'seat-index';
    seatIndex.textContent = index + 1;
    button.appendChild(seatIndex);

    if (seat.occupant) {
      button.classList.add('seat--occupied');
      const nameSpan = document.createElement('span');
      nameSpan.className = 'seat-name';
      nameSpan.textContent = seat.occupant;
      button.appendChild(nameSpan);
    }

    const isCurrentParticipant = seat.occupant === currentParticipant;
    if (isCurrentParticipant) {
      button.classList.add('seat--current');
    }

    const isSeatTakenByAnother = Boolean(seat.occupant && seat.occupant !== currentParticipant);
    if (isSeatTakenByAnother || !currentParticipant) {
      if (isSeatTakenByAnother) {
        button.classList.add('seat--disabled');
      }
      button.disabled = isSeatTakenByAnother || !currentParticipant;
    }

    const ariaLabelParts = [`Место номер ${index + 1}`];
    if (seat.occupant) {
      ariaLabelParts.push(`занято участником ${seat.occupant}`);
    } else {
      ariaLabelParts.push('свободно');
    }
    button.setAttribute('aria-label', ariaLabelParts.join(', '));

    button.addEventListener('click', () => handleSeatSelection(seat.id));
    circle.appendChild(button);
  });
}

function renderParticipantList() {
  participantList.innerHTML = '';
  const assignedSeats = seats.filter((seat) => seat.occupant);
  if (!assignedSeats.length) {
    const empty = document.createElement('li');
    empty.className = 'consultation-list__empty';
    empty.textContent = 'Пока никто не занял место';
    participantList.appendChild(empty);
    return;
  }

  assignedSeats.forEach((seat) => {
    const seatNumber = seats.indexOf(seat) + 1;
    const item = document.createElement('li');
    item.className = 'participant-list__item';

    const name = document.createElement('span');
    name.textContent = seat.occupant;
    const place = document.createElement('span');
    place.textContent = `Место №${seatNumber}`;

    item.appendChild(name);
    item.appendChild(place);
    participantList.appendChild(item);
  });
}

function handleSeatSelection(seatId) {
  if (!currentParticipant) {
    showSelectionMessage('Введите имя участника, чтобы выбрать место.', 'error');
    return;
  }

  const seat = seats.find((s) => s.id === seatId);
  if (!seat || (seat.occupant && seat.occupant !== currentParticipant)) {
    showSelectionMessage('Это место уже занято. Выберите другое.', 'error');
    return;
  }

  seats.forEach((item) => {
    if (item.occupant === currentParticipant) {
      item.occupant = null;
    }
  });

  seat.occupant = currentParticipant;
  showSelectionMessage(`${currentParticipant} занял(а) место №${seats.indexOf(seat) + 1}.`, 'success');
  participantNameInput.value = '';
  currentParticipant = null;
  renderSeats();
  renderParticipantList();
}

startSeatSelectionButton.addEventListener('click', () => {
  const name = participantNameInput.value.trim();
  if (!name) {
    showSelectionMessage('Пожалуйста, введите имя участника.', 'error');
    return;
  }

  const alreadyAssigned = seats.find((seat) => seat.occupant === name);
  if (alreadyAssigned) {
    currentParticipant = name;
    showSelectionMessage(
      `${name}, вы уже в круге. Можете выбрать другое свободное место при необходимости.`,
      'success',
    );
  } else {
    currentParticipant = name;
    showSelectionMessage(`${name}, выберите свободное место.`, 'success');
  }

  renderSeats();
});

applySeatCountButton.addEventListener('click', () => {
  const value = Number.parseInt(seatCountInput.value, 10);
  if (!Number.isInteger(value) || value < 1) {
    showSelectionMessage('Количество мест должно быть положительным числом.', 'error');
    seatCountInput.value = seats.length;
    return;
  }
  resizeSeats(value);
});

addSeatButton.addEventListener('click', () => {
  addSeat();
});

window.addEventListener('resize', () => {
  renderSeats();
});

if (participantNameInput) {
  participantNameInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      startSeatSelectionButton.click();
    }
  });
}

initializeSeats(Number.parseInt(seatCountInput.value, 10) || 8);
renderConsultations();
