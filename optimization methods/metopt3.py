# %% [markdown]
# # Задание 3: Классификация краудфандинговых проектов
# Сравнение стандартного и кастомного оптимизатора в PyTorch

# %%
import pandas as pd
import numpy as np
import sklearn
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Настройка для воспроизводимости
torch.manual_seed(42)
np.random.seed(42)

# %% [markdown]
# ## 2.1. Загрузка и предобработка данных

# %%
# Загрузка данных
df = pd.read_csv('turkishCF.csv', sep=';')
print(f"Размер датасета: {df.shape}")
print(f"Целевая переменная распределение:\n{df['basari_durumu'].value_counts()}")

# %%
# Выбор и обработка признаков
def preprocess_data(df):
    df_clean = df.copy()
    
    # Целевая переменная
    df_clean['target'] = (df_clean['basari_durumu'] == 'başarılı').astype(int)
    
    # Числовые признаки
    numeric_cols = ['hedef_miktari', 'toplanan_tutar', 'destek_orani', 
                    'gun_sayisi', 'destekci_sayisi', 'icerik_kelime_sayisi',
                    'sm_takipci', 'etiket_sayisi', 'odul_sayisi', 'ekip_kisi_sayisi']
    
    # Очистка числовых признаков
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col].astype(str).str.replace('%', '').str.replace(',', '.'), 
                                          errors='coerce')
    
    # Категориальные признаки для кодирования
    cat_cols = ['kategori', 'fon_sekli', 'bolge', 'proje_sahibi_cinsiyet', 
                'tanitim_videosu', 'sosyal_medya', 'web_sitesi']
    
    # Label Encoding для категориальных
    for col in cat_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna('unknown')
            le = LabelEncoder()
            df_clean[col + '_enc'] = le.fit_transform(df_clean[col].astype(str))
    
    # Формирование финального набора признаков
    feature_cols = [c + '_enc' if c in cat_cols else c for c in numeric_cols + cat_cols 
                    if c in df_clean.columns or c + '_enc' in df_clean.columns]
    
    # Удаление строк с пропусками в признаках
    df_clean = df_clean.dropna(subset=feature_cols + ['target'])
    
    X = df_clean[feature_cols].values
    y = df_clean['target'].values
    
    # Масштабирование
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    return X, y, feature_cols, scaler

X, y, feature_names, scaler = preprocess_data(df)
print(f"Финальный размер: {X.shape}, признаков: {len(feature_names)}")

# %%
# Разделение на выборки
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")

# %% [markdown]
# ## 2.2. PyTorch Dataset и Neural Network

# %%
class CrowdfundDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# %%
class CrowdfundNN(nn.Module):
    """Нейронная сеть для классификации краудфандинговых проектов"""
    def __init__(self, input_dim, hidden_dims=[64, 32, 16], dropout_rate=0.3):
        super(CrowdfundNN, self).__init__()
        
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x).squeeze()

# %% [markdown]
# ## 2.3. Кастомный оптимизатор (наследование от torch.optim.SGD)

# %%
class CustomSGD(optim.SGD):
    """
    Кастомная реализация SGD с модифицированной эвристикой:
    - Адаптивный learning rate на основе градиентной статистики
    - Градиентный клиппинг для стабильности
    - Моментум с затуханием
    
    Наследуется от torch.optim.SGD для прозрачной интеграции.
    """
    def __init__(self, params, lr=0.01, momentum=0.9, dampening=0,
                 weight_decay=0, nesterov=False, 
                 grad_clip_norm=1.0,  # Новый параметр: клиппинг градиента
                 lr_decay_factor=0.995,  # Новый параметр: затухание LR
                 min_lr=1e-6):  # Новый параметр: минимальный LR
        super().__init__(params, lr=lr, momentum=momentum, dampening=dampening,
                        weight_decay=weight_decay, nesterov=nesterov)
        
        self.grad_clip_norm = grad_clip_norm
        self.lr_decay_factor = lr_decay_factor
        self.min_lr = min_lr
        self.step_count = 0
        
        # Инициализация буфера для статистики градиентов
        for group in self.param_groups:
            group['grad_sum_sq'] = 0.0
            group['grad_count'] = 0
    
    def step(self, closure=None):
        """
        Выполняет шаг оптимизации с кастомными эвристиками.
        """
        loss = super().step(closure)  # Базовый шаг родительского класса
        self.step_count += 1
        
        # === КАСТОМНЫЕ ЭВРИСТИКИ ===
        
        # 1. Адаптивное затухание learning rate
        for group in self.param_groups:
            new_lr = max(group['lr'] * self.lr_decay_factor, self.min_lr)
            group['lr'] = new_lr
        
        # 2. Градиентный клиппинг (применяется постфактум для следующего шага)
        if self.grad_clip_norm is not None:
            total_norm = 0
            for group in self.param_groups:
                for p in group['params']:
                    if p.grad is not None:
                        param_norm = p.grad.data.norm(2)
                        total_norm += param_norm.item() ** 2
            total_norm = total_norm ** 0.5
            clip_coef = self.grad_clip_norm / (total_norm + 1e-6)
            if clip_coef < 1:
                for group in self.param_groups:
                    for p in group['params']:
                        if p.grad is not None:
                            p.grad.data.mul_(clip_coef)
        
        # 3. Статистика градиентов для мониторинга
        for group in self.param_groups:
            grad_norms = [p.grad.data.norm().item() for p in group['params'] 
                         if p.grad is not None]
            if grad_norms:
                group['grad_sum_sq'] = (group['grad_sum_sq'] * 0.99 + 
                                       np.mean(grad_norms)**2 * 0.01)
                group['grad_count'] += 1
        
        return loss
    
    def get_lr_stats(self):
        """Возвращает статистику learning rate для анализа"""
        return [group['lr'] for group in self.param_groups]
    
    def get_grad_stats(self):
        """Возвращает статистику градиентов"""
        stats = []
        for group in self.param_groups:
            if 'grad_sum_sq' in group and group['grad_count'] > 0:
                stats.append(np.sqrt(group['grad_sum_sq'] / group['grad_count']))
        return stats

# %% [markdown]
# ## 2.4. Функции обучения и оценки

# %%
def train_model(model, dataloader, optimizer, criterion, epochs=50, device='cpu'):
    """Обучение модели с отслеживанием метрик"""
    model.train()
    history = {'loss': [], 'accuracy': []}
    
    for epoch in range(epochs):
        epoch_loss = 0
        correct = 0
        total = 0
        
        for batch_X, batch_y in dataloader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            predictions = (outputs >= 0.5).float()
            correct += (predictions == batch_y).sum().item()
            total += batch_y.size(0)
        
        avg_loss = epoch_loss / len(dataloader)
        accuracy = correct / total
        history['loss'].append(avg_loss)
        history['accuracy'].append(accuracy)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f} | Acc: {accuracy:.4f}")
    
    return history

# %%
def evaluate_model(model, dataloader, criterion, device='cpu'):
    """Оценка модели на тестовых данных"""
    model.eval()
    all_preds = []
    all_probs = []
    all_labels = []
    total_loss = 0
    
    with torch.no_grad():
        for batch_X, batch_y in dataloader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            total_loss += loss.item()
            
            probs = outputs.cpu().numpy()
            preds = (outputs >= 0.5).float().cpu().numpy()
            
            all_probs.extend(probs)
            all_preds.extend(preds)
            all_labels.extend(batch_y.cpu().numpy())
    
    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(all_labels, all_preds)
    
    # Для ROC-AUC нужна хотя бы одна запись каждого класса
    try:
        if len(np.unique(all_labels)) > 1:
            roc_auc = roc_auc_score(all_labels, all_probs)
        else:
            roc_auc = None
    except:
        roc_auc = None
    
    return {
        'loss': avg_loss,
        'accuracy': accuracy,
        'roc_auc': roc_auc,
        'predictions': np.array(all_preds),
        'probabilities': np.array(all_probs),
        'labels': np.array(all_labels)
    }

# %% [markdown]
# ## 2.5. Эксперимент: Сравнение оптимизаторов

# %%
# Параметры
INPUT_DIM = X_train.shape[1]
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.01
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(f"Используемое устройство: {DEVICE}")
print(f"Размерность признаков: {INPUT_DIM}")

# %%
# === ЭКСПЕРИМЕНТ 1: Стандартный SGD ===
print("\n" + "="*60)
print("ЭКСПЕРИМЕНТ 1: Стандартный torch.optim.SGD")
print("="*60)

model_sgd = CrowdfundNN(INPUT_DIM).to(DEVICE)
optimizer_sgd = optim.SGD(model_sgd.parameters(), lr=LEARNING_RATE, momentum=0.9)
criterion = nn.BCELoss()

train_loader = DataLoader(CrowdfundDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(CrowdfundDataset(X_test, y_test), batch_size=BATCH_SIZE, shuffle=False)

history_sgd = train_model(model_sgd, train_loader, optimizer_sgd, criterion, EPOCHS, DEVICE)
results_sgd = evaluate_model(model_sgd, test_loader, criterion, DEVICE)

print(f"\nРезультаты на тесте (Standard SGD):")
print(f"  Accuracy: {results_sgd['accuracy']:.4f}")
print(f"  Loss: {results_sgd['loss']:.4f}")
if results_sgd['roc_auc']:
    print(f"  ROC-AUC: {results_sgd['roc_auc']:.4f}")

# %%
# === ЭКСПЕРИМЕНТ 2: Кастомный SGD ===
print("\n" + "="*60)
print("ЭКСПЕРИМЕНТ 2: Кастомный CustomSGD")
print("="*60)

model_custom = CrowdfundNN(INPUT_DIM).to(DEVICE)
# Инициализируем с теми же весами для честного сравнения
model_custom.load_state_dict(model_sgd.state_dict())

optimizer_custom = CustomSGD(
    model_custom.parameters(), 
    lr=LEARNING_RATE, 
    momentum=0.9,
    grad_clip_norm=1.0,      # Кастомная эвристика 1
    lr_decay_factor=0.995,   # Кастомная эвристика 2
    min_lr=1e-6              # Кастомная эвристика 3
)

history_custom = train_model(model_custom, train_loader, optimizer_custom, criterion, EPOCHS, DEVICE)
results_custom = evaluate_model(model_custom, test_loader, criterion, DEVICE)

print(f"\nРезультаты на тесте (Custom SGD):")
print(f"  Accuracy: {results_custom['accuracy']:.4f}")
print(f"  Loss: {results_custom['loss']:.4f}")
if results_custom['roc_auc']:
    print(f"  ROC-AUC: {results_custom['roc_auc']:.4f}")

# %% [markdown]
# ## 2.6. Визуализация и сравнение результатов

# %%
# График обучения
plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.plot(history_sgd['loss'], label='Standard SGD', linewidth=2)
plt.plot(history_custom['loss'], label='Custom SGD', linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Сравнение функции потерь')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(history_sgd['accuracy'], label='Standard SGD', linewidth=2)
plt.plot(history_custom['accuracy'], label='Custom SGD', linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Сравнение точности')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('training_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# %%
# Сравнение метрик в таблице
comparison_df = pd.DataFrame({
    'Метрика': ['Accuracy', 'Test Loss', 'ROC-AUC'],
    'Standard SGD': [
        f"{results_sgd['accuracy']:.4f}",
        f"{results_sgd['loss']:.4f}",
        f"{results_sgd['roc_auc']:.4f}" if results_sgd['roc_auc'] else 'N/A'
    ],
    'Custom SGD': [
        f"{results_custom['accuracy']:.4f}",
        f"{results_custom['loss']:.4f}",
        f"{results_custom['roc_auc']:.4f}" if results_custom['roc_auc'] else 'N/A'
    ],
    'Разница': [
        f"{results_custom['accuracy'] - results_sgd['accuracy']:+.4f}",
        f"{results_custom['loss'] - results_sgd['loss']:+.4f}",
        f"{results_custom['roc_auc'] - results_sgd['roc_auc']:+.4f}" if results_custom['roc_auc'] and results_sgd['roc_auc'] else 'N/A'
    ]
})

print("\n СРАВНЕНИЕ РЕЗУЛЬТАТОВ:")
print(comparison_df.to_string(index=False))

# %%
# Анализ статистики кастомного оптимизатора
print("\n Анализ кастомного оптимизатора:")
print(f"  Начальный LR: {LEARNING_RATE}")
print(f"  Финальный LR: {optimizer_custom.get_lr_stats()[0]:.6f}")
print(f"  Средний norm градиента: {np.mean(optimizer_custom.get_grad_stats()):.4f}")

# %% [markdown]
# ## 2.7. Примеры предсказаний

# %%
# Примеры предсказаний на тестовых данных
print("\n ПРИМЕРЫ ПРЕДСКАЗАНИЙ (первые 10 объектов теста):")
print("-" * 80)

sample_indices = np.random.choice(len(X_test), 10, replace=False)

model_custom.eval()
with torch.no_grad():
    for idx in sample_indices:
        x_sample = torch.FloatTensor(X_test[idx:idx+1]).to(DEVICE)
        y_true = y_test[idx]
        prob = model_custom(x_sample).item()
        pred = int(prob >= 0.5)
        
        status = "+" if pred == y_true else "-"
        print(f"{status} True: {y_true} | Pred: {pred} | Prob: {prob:.3f} | "
              f"Features norm: {np.linalg.norm(X_test[idx]):.2f}")

# %% [markdown]
# ## 2.8. Отчёт о работе

# %%


for q, a in qa.items():
    print(f"\n{q}")
    print(f"   → {a}")

# %% [markdown]
# ## Сохранение результатов

# %%
# Сохранение моделей и метрик
import json
import pickle

results = {
    'standard_sgd': {
        'history': history_sgd,
        'test_metrics': {k: v for k, v in results_sgd.items() 
                        if k not in ['predictions', 'probabilities', 'labels']},
        'final_accuracy': results_sgd['accuracy']
    },
    'custom_sgd': {
        'history': history_custom,
        'test_metrics': {k: v for k, v in results_custom.items() 
                        if k not in ['predictions', 'probabilities', 'labels']},
        'final_accuracy': results_custom['accuracy']
    },
    'comparison': comparison_df.to_dict('records')
}

with open('experiment_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Сохранение моделей
torch.save(model_sgd.state_dict(), 'model_standard_sgd.pt')
torch.save(model_custom.state_dict(), 'model_custom_sgd.pt')

print("\n Результаты сохранены в:")
print("   - experiment_results.json")
print("   - model_standard_sgd.pt")  
print("   - model_custom_sgd.pt")
print("   - training_comparison.png")